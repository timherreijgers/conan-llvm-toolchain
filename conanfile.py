import os
import subprocess
import re
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, save


class LlvmToolchainConan(ConanFile):
    name = "llvm-toolchain"
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

    def build(self):
        get(self, self._get_download_link(), strip_root=True)


    def package_id(self):
        self.info.settings_target = self.settings_build
        self.info.settings_target.rm_safe("compiler")
        self.info.settings_target.rm_safe("build_type")

    def package(self):
        dirs_to_copy = ["include", "lib", "share/libc++/v1"]
        for dir_name in dirs_to_copy:
            copy(self, pattern=f"{dir_name}/*", src=self.build_folder, dst=self.package_folder, keep_path=True)

        executable_patterns = ["clang(\.exe)*", "clang\+\+(\.exe)*", "llvm-ar(\.exe)*", "llvm-ranlib(\.exe)*", "llvm-strip(\.exe)*", "llvm-as(\.exe)*", "llvm-ld(\.exe)*", "clang-[0-9]+(\.exe)*", "llvm-objcopy(\.exe)*", "clang-scan-deps(\.exe)*"]
        for executable_pattern in executable_patterns:
            regex = re.compile(executable_pattern)
            bin_dir = os.path.join(self.build_folder, "bin")
            for filename in os.listdir(bin_dir):
                if regex.fullmatch(filename):
                    copy(self, pattern=f"bin/{filename}", src=self.build_folder, dst=self.package_folder, keep_path=True)


        clang_version_pattern = re.compile(r"^clang-[0-9]+$")

        bin_dir = os.path.join(self.build_folder, "bin")
        for filename in os.listdir(bin_dir):
            if clang_version_pattern.fullmatch(filename):
                copy(
                    self,
                    pattern=f"bin/{filename}",
                    src=self.build_folder,
                    dst=self.package_folder,
                    keep_path=True,
                )

        copy(self, "LICENSE", src=self.build_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = []

        if self.settings.os == "Linux":
            self.__package_info_linux()

        if self.settings.os == "Macos":
            self.__package_info_macos()

        self.conf_info.define("tools.build:compiler_executables", {
            "c": "clang",
            "cpp": "clang++",
            "ar": "llvm-ar",
            "ranlib": "llvm-ranlib",
            "strip": "llvm-strip",
            "asm": "llvm-as",
        })

    def __package_info_linux(self):
        target = "x86_64-unknown-linux-gnu" if self.settings.arch == "x86_64" else "aarch64-unknown-linux-gnu"
        include_dir = os.path.join(self.package_folder, "include", "c++", "v1")
        target_include_dir = os.path.join(self.package_folder, "include", target, "c++", "v1")
        lib_dir = os.path.join(self.package_folder, "lib", target)

        self.conf_info.define("tools.build:cxxflags", [
            "-nostdinc++",
            "-isystem",
            include_dir,
            "-isystem",
            target_include_dir,
        ])
        link_flags = [
            f"-L{lib_dir}",
            "-lc++",
        ]
        self.conf_info.define("tools.build:exelinkflags", link_flags)
        self.conf_info.define("tools.build:sharedlinkflags", link_flags)
        self.buildenv_info.append_path("LD_LIBRARY_PATH", lib_dir)

    def __package_info_macos(self):
        include_dir = os.path.join(self.package_folder, "include", "c++", "v1")
        self.conf_info.define("tools.build:cxxflags", [
            "-nostdinc++",
            "-isystem",
            include_dir,
        ])

        sdk_path = self.conf.get("tools.apple:sdk_path")
        if not sdk_path:
            sdk_path = subprocess.check_output(
                ["xcrun", "--sdk", "macosx", "--show-sdk-path"],
                text=True,
            ).strip()

        self.buildenv_info.define("SDKROOT", sdk_path)

        lib_dir = os.path.join(self.package_folder, "lib")
        link_flags = [
            f"-L{lib_dir}",
            f"-Wl,-rpath,{lib_dir}",
            "-lc++abi",
            "-lunwind",
            # dyld can coalesce symbols with system libc++; ensure it is initialized.
            "-Wl,-needed_library,/usr/lib/libc++.1.dylib",
        ]
        self.conf_info.define("tools.build:exelinkflags", link_flags)
        self.conf_info.define("tools.build:sharedlinkflags", link_flags)
