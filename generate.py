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

    # Sort assets by name to ensure we get the latest macOS version if multiple exist
    assets.sort(key=lambda x: x['name'], reverse=True)

    for asset in assets:
        if 'macos' in asset['name'] and arch in asset['name'] and '.tar.xz' in asset['name']:
            # We found a matching asset.
            url = asset['browser_download_url']
            sha256 = asset['digest'].split(':')[1]
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

    # The python version is tied to the frozen executable. We'll use the latest
    # version that works for the bundled app. As per the error message, this is 3.13.
    python_version = "3.13"

    # --- Start of Homebrew Formula Template ---
    formula_template = f"""# frozen_string_literal: true

class Gam < Formula
  desc "Command-line tool for Google Workspace admins"
  homepage "https://github.com/GAM-team/GAM"
  version "{version}"
  license "Apache-2.0"

  # We need to install the full Python distribution to ensure all standard
  # libraries are available to the bundled gam executable.
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
    # The downloaded tar.xz archive contains the 'gam' executable.
    # We install it to the Homebrew `libexec` directory.
    libexec.install "gam"

    # Now, install the entire Homebrew Python installation as a dependency,
    # and symlink all its files into the `libexec` directory.
    # This ensures that the bundled `gam` executable can find all the
    # standard Python libraries it needs.
    libexec.install_symlink Dir[Formula["python@{python_version}"].opt_prefix/"*"]

    # We create a shim script to correctly set the PYTHONHOME environment variable
    # before executing the gam binary. This tells the Python interpreter where
    # to find its standard library modules (like 'encodings').
    (bin/"gam").write_env_script(libexec/"gam",
      # PYTHONHOME needs to point to the root of the Python installation.
      PYTHONHOME: Formula["python@{python_version}"].opt_prefix
    )
  end

  test do
    system "#{bin}/gam", "version"
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