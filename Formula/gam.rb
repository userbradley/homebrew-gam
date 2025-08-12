# frozen_string_literal: true

class Gam < Formula
  desc "Command-line tool for Google Workspace admins"
  homepage "https://github.com/GAM-team/GAM"
  version "7.18.03"
  license "Apache-2.0"

  on_arm do
    url "https://github.com/GAM-team/GAM/releases/download/v7.18.03/gam-7.18.03-macos15.5-arm64.tar.xz"
    sha256 "7b518b300b2dea8b410a6ba81c943c1965044ee3811531b996f438759a3559f0"
  end

  on_intel do
    url "https://github.com/GAM-team/GAM/releases/download/v7.18.03/gam-7.18.03-macos13.7-x86_64.tar.xz"
    sha256 "b77f409533446d515141935862db11507f4585d378a91d72f45369b166c59497"
  end

  def install
    libexec.install "gam"
    bin.install_symlink libexec/"gam"
  end

  test do
    system "{bin}/gam", "version"
  end
end
