# frozen_string_literal: true

class Gam < Formula
  desc "Command-line tool for Google Workspace admins"
  homepage "https://github.com/GAM-team/GAM"
  version "7.18.03"
  license "Apache-2.0"

  # The 'gam' installation package is a self-contained archive that includes its own
  # frozen Python environment. Therefore, we do not need to declare a dependency on
  # Homebrew's Python formula.
  # The 'gam' executable expects its associated files to be in a specific relative path.

  on_arm do
    url "https://github.com/GAM-team/GAM/releases/download/v7.18.03/gam-7.18.03-macos15.5-arm64.tar.xz"
    sha256 "7b518b300b2dea8b410a6ba81c943c1965044ee38e11531b996f438759a3559f0"
  end

  on_intel do
    url "https://github.com/GAM-team/GAM/releases/download/v7.18.03/gam-7.18.03-macos13.7-x86_64.tar.xz"
    sha256 "b77f409533446d515141935862db11507f4585d378a91d72f45369b166c59497"
  end

  def install
    # The downloaded archive contains a directory named "gam".
    # We install the entire contents of this directory into the libexec folder.
    libexec.install Dir["*"]

    # The 'gam' executable is a file inside the directory we just installed.
    # We create a symlink from this executable to the Homebrew 'bin' directory.
    # This makes 'gam' available on the user's PATH.
    bin.install_symlink libexec/"gam"
  end

  test do
    system bin/"gam", "version"
  end
end