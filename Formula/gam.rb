# frozen_string_literal: true

class Gam < Formula
  desc "Command-line tool for Google Workspace admins"
  homepage "https://github.com/GAM-team/GAM"
  version "7.18.03"
  license "Apache-2.0"

  depends_on "python@3.13"

  on_arm do
    url "https://github.com/GAM-team/GAM/releases/download/v7.18.03/gam-7.18.03-macos15.5-arm64.tar.xz"
    sha256 "7b518b300b2dea8b410a6ba81c943c1965044ee3811531b996f438759a3559f0"
  end

  on_intel do
    url "https://github.com/GAM-team/GAM/releases/download/v7.18.03/gam-7.18.03-macos13.7-x86_64.tar.xz"
    sha256 "b77f409533446d515141935862db11507f4585d378a91d72f45369b166c59497"
  end

  def install
    # Install the 'gam' executable to the libexec directory
    libexec.install "gam"

    # Symlink the Python shared library from the Homebrew Python installation
    # to the location where 'gam' expects it to be.
    # This resolves the 'no such file' error for libpython3.13.dylib.
    python_lib_path = Formula["python@3.13"].opt_prefix/"Frameworks/Python.framework/Versions/3.13/lib/libpython3.13.dylib"
    mkdir_p libexec/"lib"
    ln_s python_lib_path, libexec/"lib/"

    # Symlink the gam executable to the Homebrew bin directory
    bin.install_symlink libexec/"gam"
  end

  test do
    system "{bin}/gam", "version"
  end
end
