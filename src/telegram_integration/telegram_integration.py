import tempfile
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ContentType
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from speech_recognition.diarization.resemblyzer_with_silero_vad_diarization_service import (
    ResemblyzerWithSileroVADDiarizationService,
)
from speech_recognition.interval_storage.intervaltree_storage_service import IntervalTreeStorageService
from speech_recognition.media.ffmpeg.ffmpeg_preparation_service import FfmpegPreparationService
from speech_recognition.output.full_output_pipeline import FullOutputPipeline
from speech_recognition.pipeline.pipeline import TranscriptionPipeline
from speech_recognition.transcription.faster_whisper_service import FasterWhisperTranscriptionService

from .progress_observer import TelegramProgressObserver

preparation_service = FfmpegPreparationService()
diarization_service = ResemblyzerWithSileroVADDiarizationService()
transcription_service = FasterWhisperTranscriptionService()


def get_pipeline(  # noqa: D103
    output: FullOutputPipeline,
    observer: TelegramProgressObserver,
) -> TranscriptionPipeline:
    return TranscriptionPipeline(
        preparation_service,
        diarization_service,
        transcription_service,
        IntervalTreeStorageService(),
        output,
        observer,
    )


# TODO(0xfee1dead): refactoring https://github.com/0xFEE1DEAD/hush_transcribe_service/issues/1  # noqa: FIX002
class TelegramBotApp:
    def __init__(self, token: str) -> None:
        """Init telegram bot."""
        self.bot = Bot(token)
        self.dp = Dispatcher()
        self.router = Router()

        self.__register_handlers()
        self.dp.include_router(self.router)

    def __register_handlers(self) -> None:
        @self.router.message(CommandStart())
        async def start_cmd(message: Message) -> None:  # pyright: ignore[reportUnusedFunction]
            await message.answer("👋 Привет! Отправь мне файл, и я его обработаю.")  # noqa: RUF001

        @self.router.message(
            F.content_type.in_(
                {
                    ContentType.PHOTO,
                    ContentType.VIDEO,
                    ContentType.DOCUMENT,
                    ContentType.AUDIO,
                    ContentType.VOICE,
                    ContentType.VIDEO_NOTE,
                },
            ),
        )
        async def handle_media(message: Message, state: FSMContext) -> None:  # pyright: ignore[reportUnusedFunction]
            file_id = self.__extract_file_id(message)

            if file_id is None:
                await message.answer("Ой, кажется не удалось получить файл, попробуй загрузить снова")
                return

            await state.update_data(file_id=file_id)

            speakers_keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Авто")],
                    [
                        KeyboardButton(text="2"),
                        KeyboardButton(text="3"),
                        KeyboardButton(text="4"),
                        KeyboardButton(text="5"),
                    ],
                ],
                resize_keyboard=True,
                one_time_keyboard=True,
            )

            # спрашиваем количество собеседников
            await message.answer("Выбери количество собеседников:", reply_markup=speakers_keyboard)

            # переходим в состояние
            await state.set_state(DialogStates.waiting_for_speakers)

        @self.router.message(DialogStates.waiting_for_speakers, F.text.in_(["Авто", "2", "3", "4", "5"]))
        async def process_speakers_choice(message: Message, state: FSMContext) -> None:  # pyright: ignore[reportUnusedFunction]
            user_choice = message.text
            speakers = None if user_choice == "Авто" or user_choice is None else int(user_choice)
            data = await state.get_data()
            file_id = data["file_id"]
            tg_file = await self.bot.get_file(file_id)

            if tg_file.file_path is None:
                await message.answer("Ой, кажется не удалось получить файл, попробуй загрузить снова")
                return

            await message.answer("Начинаю обработку…", reply_markup=ReplyKeyboardRemove())

            with tempfile.TemporaryDirectory() as tmpdir:
                progress_message = await message.answer("Получаю файл, пожалуйста подожди.")
                local_path = Path(tmpdir) / Path(file_id)
                await self.bot.download_file(tg_file.file_path, local_path)

                observer = TelegramProgressObserver(progress_message)
                csv_path = tmpdir / Path("transcribed.csv")
                txt_path = tmpdir / Path("transcribed.txt")
                simple_txt_path = tmpdir / Path("transcribed-simple.txt")

                async with FullOutputPipeline(csv_path, txt_path, simple_txt_path) as output:
                    pipeline = get_pipeline(
                        output,
                        observer,
                    )

                    await pipeline.run_pipeline(Path(local_path), speakers)

                await message.answer_document(FSInputFile(csv_path))
                await message.answer_document(FSInputFile(txt_path))
                await message.answer_document(FSInputFile(simple_txt_path))

            await state.clear()

    def __extract_file_id(self, message: Message) -> str | None:  # noqa: PLR0911
        if message.photo:
            return message.photo[-1].file_id
        if message.video:
            return message.video.file_id
        if message.document:
            return message.document.file_id
        if message.audio:
            return message.audio.file_id
        if message.voice:
            return message.voice.file_id
        if message.video_note:
            return message.video_note.file_id

        return None

    async def run(self) -> None:
        await self.dp.start_polling(self.bot)  # pyright: ignore[reportUnknownMemberType]


class DialogStates(StatesGroup):
    waiting_for_speakers = State()
    waiting_for_file = State()
