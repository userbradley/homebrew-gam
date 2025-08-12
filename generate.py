import requests
import json
import sys

def get_latest_gam_release_info():
    """
    Fetches the latest GAM release data from the GitHub API.
    Returns the JSON data or None on failure.
    """
    github_api_url = "https://api.github.com/repos/GAM-team/GAM/releases/latest"

    try:
        response = requests.get(github_api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub API: {e}", file=sys.stderr)
        return None

def find_asset_info(assets, arch):
    """
    Finds the download URL and SHA256 checksum for a specific architecture.
    """
    url = None
    sha256 = None

    # The digest property is always `sha256:HEX_VALUE`
    for asset in assets:
        if 'macos' in asset['name'] and arch in asset['name'] and '.tar.xz' in asset['name']:
            url = asset['browser_download_url']
            sha256 = asset['digest'].split(':')[-1]
            break

    return url, sha256

def generate_gam_formula():
    """
    Generates a Homebrew formula file named 'gam.rb'.
    """
    release_data = get_latest_gam_release_info()
    if not release_data:
        return

    # Extract version from the tag name, e.g., 'v7.18.03' -> '7.18.03'
    version = release_data['tag_name'].lstrip('v')

    # Find assets for both macOS architectures
    arm64_url, arm64_sha256 = find_asset_info(release_data['assets'], 'arm64')
    x86_64_url, x86_64_sha256 = find_asset_info(release_data['assets'], 'x86_64')

    if not arm64_url or not x86_64_url:
        print("Could not find required macOS release assets in the latest release.", file=sys.stderr)
        return

    # --- Start of Homebrew Formula Template ---
    formula_template = f"""# frozen_string_literal: true

class Gam < Formula
  desc "Command-line tool for Google Workspace admins"
  homepage "https://github.com/GAM-team/GAM"
  version "{version}"
  license "Apache-2.0"

  # The 'gam' installation package is a self-contained archive that includes its own
  # frozen Python environment. Therefore, we do not need to declare a dependency on
  # Homebrew's Python formula.
  # The 'gam' executable expects its associated files to be in a specific relative path.

  on_arm do
    url "{arm64_url}"
    sha256 "{arm64_sha256}"
  end

  on_intel do
    url "{x86_64_url}"
    sha256 "{x86_64_sha256}"
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
"""
    # --- End of Homebrew Formula Template ---

    # Write the content to the gam.rb file
    try:
        with open("Formula/gam.rb", "w") as f:
            f.write(formula_template)
        print("Successfully generated gam.rb file with the latest release information.")
    except IOError as e:
        print(f"Error writing to gam.rb file: {e}", file=sys.stderr)

if __name__ == "__main__":
    generate_gam_formula()