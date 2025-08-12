# frozen_string_literal: true

class Gam < Formula
  desc "Command-line tool for Google Workspace admins"
  homepage "https://github.com/GAM-team/GAM"
  version "7.18.03"
  license "Apache-2.0"

  # We need to install the full Python distribution to ensure all standard
  # libraries are available to the bundled gam executable.
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
    # The downloaded tar.xz archive contains the 'gam' executable.
    # We install it to the Homebrew `libexec` directory.
    libexec.install "gam"

    # Now, install the entire Homebrew Python installation as a dependency,
    # and symlink all its files into the `libexec` directory.
    # This ensures that the bundled `gam` executable can find all the
    # standard Python libraries it needs.
    libexec.install_symlink Dir[Formula["python@3.11"].opt_prefix/"*"]

    # We create a shim script to correctly set the PYTHONHOME environment variable
    # before executing the gam binary. This tells the Python interpreter where
    # to find its standard library modules (like 'encodings').
    (bin/"gam").write_env_script(libexec/"gam",
      # PYTHONHOME needs to point to the root of the Python installation.
      PYTHONHOME: Formula["python@3.11"].opt_prefix
    )
  end

  test do
    system "#<built-in function bin>/gam", "version"
  end
end
