from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel, Field, HttpUrl


class DownloadLink(BaseModel):
    name: str = Field(..., description="Текст на кнопке ссылки")
    url: HttpUrl = Field(..., description="Прямая валидная HTTPS-ссылка")


class InstructionData(BaseModel):
    label: str = Field(..., description="Название платформы с эмодзи")
    text: str = Field(..., description="Текст инструкции (поддерживает HTML)")
    downloads: list[DownloadLink] = Field(
        default_factory=list, description="Список кнопок со ссылками"
    )


class PlatformInstructionsConfig(BaseModel):
    ios: InstructionData
    android: InstructionData
    windows: InstructionData
    macos: InstructionData
    android_tv: InstructionData
    apple_tv: InstructionData

    @classmethod
    def load_from_yaml(
        cls, file_path: str | Path = "src/common/instructions.yaml"
    ) -> Self:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(
                f"Файл инструкций не найден по пути: {path.absolute()}"
            )

        with open(path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)

        return cls.model_validate(raw_data)


platform_instructions = PlatformInstructionsConfig.load_from_yaml()
