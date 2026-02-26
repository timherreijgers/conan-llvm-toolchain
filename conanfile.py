import os
import subprocess
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rm, save

class LlvmToolchainConan(ConanFile):
    name = "llvm-toolchain"
    version = "20.1.0"
    settings = "os", "arch"
    package_type = "application"

    _supported_archs = ["x86_64", "armv8", "armv8.3"]
    _supported_os = ["Macos", "Linux", "Windows"]

    def _archs64(self):
        return ["armv8", "armv8.3"]

    def _get_download_link(self):
        if self.settings.os == "Macos" and self.settings.arch in self._archs64():
            return f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/LLVM-{self.version}-macOS-ARM64.tar.xz"
        elif self.settings.os == "Linux" and self.settings.arch in self._archs64():
            return f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/LLVM-{self.version}-Linux-ARM64.tar.xz"
        elif self.settings.os == "Linux" and self.settings.arch not in self._archs64():
            return f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/LLVM-{self.version}-Linux-X64.tar.xz"
        elif self.settings.os == "Windows" and self.settings.arch in self._archs64():
            return f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang+llvm-{self.version}-aarch64-pc-windows-msvc.tar.xz"
        elif self.settings.os == "Windows" and self.settings.arch not in self._archs64():
            return f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang+llvm-{self.version}-x86_64-pc-windows-msvc.tar.xz"

        raise ConanInvalidConfiguration(f"Found invalid configuration after the validate step. Os: {self.settings.os}, Architecture: {self.settings.arch}")

    def validate(self):
        if self.settings.os not in self._supported_os:
            raise ConanInvalidConfiguration(f"{self.settings.os} is not any of the supported: {self._supported_os}")

        if self.settings.arch not in self._supported_archs:
            raise ConanInvalidConfiguration(f"{self.settings.arch} is not any of the supported: {self._supported_archs}")

        if self.settings.os == "Macos" and self.settings.arch not in self._archs64():
            raise ConanInvalidConfiguration(f"{self.settings.arch} is not supported on Macos: {self._archs64()}")

    def source(self):
        save(self, "LICENSE", "LLVM Toolchain\n"
             "License: Apache License v2.0 with LLVM Exceptions\n"
             "https://github.com/llvm/llvm-project/blob/main/LICENSE.TXT")
        pass

    def build(self):
        if self.settings.os == "Macos":
            get(self,
                f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/LLVM-{self.version}-macOS-ARM64.tar.xz",
                strip_root=True)
        elif self.settings.os == "Linux":
            get(self,
                f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/LLVM-{self.version}-Linux-X64.tar.xz",
                strip_root=True)
        elif self.settings.os == "Windows":
            get(self,
                f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/clang+llvm-{self.version}-x86_64-pc-windows-msvc.tar.xz",
                strip_root=True)
        else:
            raise ConanInvalidConfiguration("Configuration not supported")


    def package_id(self):
        self.info.settings_target = self.settings_target
        self.info.settings_target.rm_safe("os")
        self.info.settings_target.rm_safe("compiler")
        self.info.settings_target.rm_safe("build_type")

    def package(self):
        dirs_to_copy = ["bin", "include", "lib", "libexec"]
        for dir_name in dirs_to_copy:
            copy(self, pattern=f"{dir_name}/*", src=self.build_folder, dst=self.package_folder, keep_path=True)

        if self.settings.os == "Macos":
            libdir = os.path.join(self.package_folder, "lib")
            for pattern in ("libc++.dylib", "libc++.1.dylib", "libc++.1.0.dylib", "libc++abi.dylib", "libc++abi.1.dylib", "libc++abi.1.0.dylib"):
                rm(self, pattern=pattern, folder=libdir, recursive=False)
        
        copy(self, "LICENSE", src=self.build_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_info(self):
        if self.settings.os == "Macos":
            self.__package_info_macos()
        else:
            self.__package_info_non_macos()

    def __package_info_non_macos(self):
        self.cpp_info.bindirs.append(os.path.join(self.package_folder, "bin"))

        self.conf_info.define("tools.build:compiler_executables", {
            "c": "clang",
            "cpp": "clang++",
            "ar": "llvm-ar",
            "ranlib": "llvm-ranlib",
            "strip": "llvm-strip",
            "asm": "llvm-as",
            "ld": "llvm-ld"
        })


    def __package_info_macos(self):
        self.cpp_info.bindirs.append(os.path.join(self.package_folder, "bin"))

        sdk_path = self.conf.get("tools.apple:sdk_path")
        if not sdk_path:
            try:
                sdk_path = subprocess.check_output(["xcrun", "--sdk", "macosx", "--show-sdk-path"]).decode(
                    "utf-8").strip()
            except Exception:
                pass

        self.buildenv_info.define("SDKROOT", sdk_path)

        self.conf_info.define("tools.build:compiler_executables", {
            "c": "clang",
            "cpp": "clang++",
        })