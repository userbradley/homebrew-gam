import requests
import json

def generate_gam_formula():
    """
    Fetches the latest GAM release data from the GitHub API and generates a
    Homebrew formula file named 'gam.rb'.
    """
    github_api_url = "https://api.github.com/repos/GAM-team/GAM/releases/latest"

    try:
        response = requests.get(github_api_url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        release_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from GitHub API: {e}")
        return

    # Extract relevant information
    version = release_data['tag_name'].lstrip('v')

    # Initialize variables for the URLs and checksums
    arm64_url = None
    arm64_sha256 = None
    x86_64_url = None
    x86_64_sha256 = None

    # Find the correct assets for macOS
    for asset in release_data['assets']:
        if 'macos' in asset['name'] and 'arm64' in asset['name'] and '.tar.xz' in asset['name']:
            arm64_url = asset['browser_download_url']
            # The digest is in the format "sha256:checksum", so we split to get the value
            arm64_sha256 = asset['digest'].split(':')[1]
        elif 'macos' in asset['name'] and 'x86_64' in asset['name'] and '.tar.xz' in asset['name']:
            x86_64_url = asset['browser_download_url']
            x86_64_sha256 = asset['digest'].split(':')[1]

    if not arm64_url or not x86_64_url:
        print("Could not find required macOS release assets in the latest release.")
        return

    # --- Start of Homebrew Formula Template ---
    formula_template = f"""# frozen_string_literal: true

class Gam < Formula
  desc "Command-line tool for Google Workspace admins"
  homepage "https://github.com/GAM-team/GAM"
  version "{version}"
  license "Apache-2.0"

  on_arm do
    url "{arm64_url}"
    sha256 "{arm64_sha256}"
  end

  on_intel do
    url "{x86_64_url}"
    sha256 "{x86_64_sha256}"
  end

  def install
    libexec.install "gam"
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
        print(f"Error writing to gam.rb file: {e}")

if __name__ == "__main__":
    generate_gam_formula()