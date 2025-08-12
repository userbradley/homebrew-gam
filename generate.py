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

def find_latest_macos_asset(assets, arch):
    """
    Finds the download URL and SHA256 checksum for the latest macOS version.
    """
    latest_asset = None
    latest_version = (0, 0)

    for asset in assets:
        if "macos" in asset["name"] and arch in asset["name"] and ".tar.xz" in asset["name"]:
            # Extract macOS version from the filename (e.g., "macos15.5")
            version_str = asset["name"].split("-macos")[-1].split(f"-{arch}")[0]
            try:
                major, minor = map(int, version_str.split("."))
                current_version = (major, minor)

                if current_version > latest_version:
                    latest_version = current_version
                    latest_asset = asset
            except ValueError:
                # Ignore assets with non-standard version strings
                continue

    if latest_asset:
        url = latest_asset["browser_download_url"]
        sha256 = latest_asset["digest"].split(":")[1]
        return url, sha256

    return None, None

def generate_gam_formula():
    """
    Generates a Homebrew formula file named 'gam.rb'.
    """
    release_data = get_latest_gam_release_info()
    if not release_data:
        return

    version = release_data['tag_name'].lstrip('v')

    # Find the latest macOS assets for each architecture
    arm64_url, arm64_sha256 = find_latest_macos_asset(release_data['assets'], "arm64")
    x86_64_url, x86_64_sha256 = find_latest_macos_asset(release_data['assets'], "x86_64")

    if not arm64_url or not x86_64_url:
        print("Could not find required macOS release assets in the latest release.", file=sys.stderr)
        return

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
    # The downloaded archive contains a single directory named "gam".
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

    try:
        with open("Formula/gam.rb", "w") as f:
            f.write(formula_template)
        print("Successfully generated gam.rb file with the latest release information.")
    except IOError as e:
        print(f"Error writing to gam.rb file: {e}", file=sys.stderr)

if __name__ == "__main__":
    generate_gam_formula()