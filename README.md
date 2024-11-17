```markdown
<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <img src="https://i.ibb.co/ryJFvnN/PDFTool.png" alt="Vector" height="200"/>
  <h3 align="center">SimplePDFTool</h3>

  <p align="center">
    A straightforward tool for PDF decryption and image extraction.
    <br />
    <a href="https://github.com/54dbd/SimplePDFTool/issues">Report Bug</a>
  </p>
</div>

<!-- ABOUT THE PROJECT -->

## About The Project

**CAUTION:** 

DECRYPTED PDF FILES WILL NO LONGER BEING AUTHENTICATED. PLEASE USE IT LEGALLY.

This project will remove the password from the PDF file, which may violate the copyright law. Please use it legally.

**SimplePDFTool** is a lightweight utility designed to simplify working with PDFs by focusing on two key features:
1. **Decryption:** Remove restrictions or passwords from PDFs to unlock their full potential.
2. **Image Extraction:** Extract embedded images from PDF files for use in other applications or analysis.

Whether you're a researcher, designer, or casual user, this tool streamlines common PDF workflows.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

This project is built for **Python 3.9+** and provides a smooth setup for anyone familiar with Python.

### Prerequisites

Ensure you have the following installed:
- Python 3.9 or higher


### Usage

- **Open GUI:**
   ```sh
   python StampExtract.py
   ```
   
   
- **Build using pyinstaller:**

    You should replace the path of the `tkinterdnd2`package in both `--paths` and `--add-data` with your own path.

   ```sh
   pyinstaller StampExtract.spec
   ```

   or 

    ```sh
    #Replace {Path/to/envs/site-packages} with your own path to the site-packages folder of your Python environment.

    pyinstaller -F StampExtract.py --paths {Path/to/envs/site-packages} --add-data "{Path/to/tkinterdnd2};tkinterdnd2" --hidden-import=tkinterdnd2 --clean --windowed

    #Example for Windows

    pyinstaller -F StampExtract.py --paths C:\Users\84555\AppData\Local\anaconda3\envs\pyinstaller\Lib\site-packages --add-data "C:\Users\84555\AppData\Local\anaconda3\envs\pyinstaller\Lib\site-packages\tkinterdnd2;tkinterdnd2" --hidden-import=tkinterdnd2 --clean --windowed
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [x] PDF decryption
- [x] Image extraction
- [x] Multi-page image extraction as a batch
- [x] GUI support for non-technical users
- [ ] Support for additional output formats
- [ ] Support for English

See the [open issues](https://github.com/54dbd/SimplePDFTool/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

We welcome contributions to enhance **SimplePDFTool**! If you'd like to contribute:
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add some NewFeature'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.

Contributors:
- 54dbd

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the GPL-3.0 License. See `LICENSE.txt` for more information.


[contributors-shield]: https://img.shields.io/github/contributors/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge

[contributors-url]: https://github.com/54dbd/Bibtex-to-gbt7714/graphs/contributors

[forks-shield]: https://img.shields.io/github/forks/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge

[forks-url]: https://github.com/54dbd/Bibtex-to-gbt7714/network/members

[stars-shield]: https://img.shields.io/github/stars/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge

[stars-url]: https://github.com/54dbd/Bibtex-to-gbt7714/stargazers

[issues-shield]: https://img.shields.io/github/issues/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge

[issues-url]: https://github.com/54dbd/Bibtex-to-gbt7714/issues

[license-shield]: https://img.shields.io/github/license/54dbd/Bibtex-to-gbt7714.svg?style=for-the-badge

[license-url]: https://github.com/54dbd/Bibtex-to-gbt7714/blob/master/LICENSE.txt

[patreon-shield]: https://img.shields.io/badge/-patreon-black.svg?style=for-the-badge&logo=patreon&colorB=555

[patreon-url]: https://patreon.com/ross376