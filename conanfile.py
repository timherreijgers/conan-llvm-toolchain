import os
import subprocess
from conan import ConanFile
from conan.tools.files import get, copy, rm
from conan.tools.apple import is_apple_os

class LlvmToolchainConan(ConanFile):
    name = "llvm-toolchain"
    version = "20.1.0"
    settings = "os", "arch"
    package_type = "application"

    def validate(self):
        pass

    def source(self):
        pass

    def build(self):
        if is_apple_os(self):
            get(self,
                f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/LLVM-{self.version}-macOS-ARM64.tar.xz",
                strip_root=True)
        else:
            get(self,
                f"https://github.com/llvm/llvm-project/releases/download/llvmorg-{self.version}/LLVM-{self.version}-Linux-X64.tar.xz",
                strip_root=True)

    def package_id(self):
        self.info.settings_target = self.settings_target
        self.info.settings_target.rm_safe("os")
        self.info.settings_target.rm_safe("compiler")
        self.info.settings_target.rm_safe("build_type")

    def package(self):
        dirs_to_copy = ["bin", "include", "lib", "libexec"]
        for dir_name in dirs_to_copy:
            copy(self, pattern=f"{dir_name}/*", src=self.build_folder, dst=self.package_folder, keep_path=True)

        if is_apple_os(self):
            libdir = os.path.join(self.package_folder, "lib")
            for pattern in ("libc++.dylib", "libc++.1.dylib", "libc++.1.0.dylib", "libc++abi.dylib", "libc++abi.1.dylib", "libc++abi.1.0.dylib"):
                rm(self, pattern=pattern, folder=libdir, recursive=False)
        
        # Copy license?

    def package_info(self):
        if is_apple_os(self):
            self.__package_info_macos()
        else:
            self.__package_info_linux()

    def __package_info_linux(self):
        self.cpp_info.bindirs.append(os.path.join(self.package_folder, "bin"))

        self.conf_info.define("tools.build:compiler_executables", {
            "c": "clang",
            "cpp": "clang++",
            "ar": "llvm-ar",
            "ranlib": "llvm-ranlib",
            "strip": "llvm-strip",
            "asm": "llvm-as",
            "ld": "llvm-ld"})


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