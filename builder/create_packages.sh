#!/bin/sh


#for version in "20.1.8" "21.1.8" "22.1.8" "23.1.1"; do
for version in "22.1.8"; do

#    if conan list "llvm-toolchain/$version:*" -r=tims-conan-local 2>/dev/null | grep -q "llvm-toolchain/$version"; then
#        echo "llvm-toolchain/$version already exists in tims-conan, skipping."
#        continue
#    fi

    echo "Creating llvm-toolchain/$version..."

    export LLVM_VERSION=${version%%.*}

    conan create .. --version=$version -pr:a=linux-x86_64.jinja
#    conan create .. --version=$version -pr:a=linux-armv8.jinja
#    conan create .. --version=$version -pr:a=win-x86_64.jinja
#    conan create .. --version=$version -pr:a=win-armv8.jinja
#    conan create .. --version=$version -pr:a=macos-armv8.jinja

#    conan upload -r tims-conan-local "llvm-toolchain/$version"

done
