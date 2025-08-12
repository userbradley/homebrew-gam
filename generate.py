import requests
import json
import sys

def generate_gam_formula():
    """
    Fetches the latest GAM release data from the GitHub API and generates a
    Homebrew formula file named 'gam.rb', including Python dependency and symlink logic.
    """
    github_api_url = "https://api.github.com/repos/GAM-team/GAM/releases/latest"

    try:
        response = requests.get(github_api_url)
        response.raise_for_status()
        release_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub API: {e}", file=sys.stderr)
        return

    # Extract relevant information
    version = release_data['tag_name'].lstrip('v')

    # Initialize variables for the URLs and checksums
    arm64_url = None
    arm64_sha256 = None
    x86_64_url = None
    x86_64_sha256 = None

    # Python version is hardcoded as per the error message.
    # In a more advanced script, you might parse the version from the asset names.
    python_version = "3.13"

    # Find the correct assets for macOS
    # Note: We're looking for the specific macOS version-dependent assets
    # as per the example in the previous conversation.
    for asset in release_data['assets']:
        if 'macos' in asset['name'] and 'arm64' in asset['name'] and '.tar.xz' in asset['name']:
            arm64_url = asset['browser_download_url']
            arm64_sha256 = asset['digest'].split(':')[1]
        elif 'macos' in asset['name'] and 'x86_64' in asset['name'] and '.tar.xz' in asset['name']:
            x86_64_url = asset['browser_download_url']
            x86_64_sha256 = asset['digest'].split(':')[1]

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

  depends_on "python@{python_version}"

  on_arm do
    url "{arm64_url}"
    sha256 "{arm64_sha256}"
  end

  on_intel do
    url "{x86_64_url}"
    sha256 "{x86_64_sha256}"
  end

  def install
    # Install the 'gam' executable to the libexec directory
    libexec.install "gam"

    # Symlink the Python shared library from the Homebrew Python installation
    # to the location where 'gam' expects it to be.
    # This resolves the 'no such file' error for libpython3.13.dylib.
    python_lib_path = Formula["python@{python_version}"].opt_prefix/"Frameworks/Python.framework/Versions/{python_version}/lib/libpython{python_version}.dylib"
    mkdir_p libexec/"lib"
    ln_s python_lib_path, libexec/"lib/"

    # Symlink the gam executable to the Homebrew bin directory
    bin.install_symlink libexec/"gam"
  end

  test do
    system "{{bin}}/gam", "version"
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