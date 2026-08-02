from enum import Enum


class PlatformInstruction(Enum):
    IOS = ("🍏 iOS", "Заглушка что бы установить")
    ANDROID = ("🤖 Android", "Андроид скачать компьютер")
    WINDOWS = ("💻 Windows", "Виндовс установить скачать компьютер 2001")
    MACOS = ("🍏 macOS", "Скачать впн на компьютер яблоко")
    ANDROID_TV = ("📺 Android TV", "Телевизор смотреть майнкрафт онлайн")
    APPLE_TV = (
        "🍎 Apple TV",
        "Скачать впн телевизор яблоко смотреть майнкрафт куплинов",
    )

    @property
    def label(self) -> str:
        """Название для кнопки."""
        return self.value[0]

    @property
    def text(self) -> str:
        """Текст инструкции."""
        return self.value[1]
