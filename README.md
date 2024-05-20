<a name="readme-top"></a>

<!-- Title -->
<div align="center">
<h3 align="center">Secure GUI Chat App</h3>

  <p align="center">
    A simple chat application that encrypts traffic through DHE
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This chat application was built as a learning project where I got to learn how to use sockets for networking, arrange my own class for encryption, and modify a database to fit the needs of my application. Despite having 'Secure' in the project name it sould be noted 
that DHE (Diffie-Hellman Key Exchange) is not secure under modern security standards, as it does not authenticate either party involved in the exchange. However, as the first public-key encryption scheme it seemed like an appropriate place to start applying the cryptographic concepts I learned in university. 

Originally, I intended to implement this as a CLI apllication, but after some deliberation I concluded that it would also serve as a good opportunity to familiarize myself with some of the graphical tools available in Python. I initially started developing the GUI with `tkinter`, but in the pursuit of more modern looking widgets I settled on using `customtkinter`, which had the advantage of operating almost identically to `tkinter`. 

I used `sqlite` for the database and created a class called `ChatDatabase` that I populated with methods for interacting with the database. My goal was to keep this logic separate from the server such that the server logic would center around networking while `ChatDatabase` would be responsible for ensuring proper database operations. When you first launch the server it'll invoke the `init_database.py` script which initializes the database and populates some default profiles.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Built With

* socket
* select
* threading
* os
* time
* logging
* random
* customtkinter
* sqlite3

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

To get a local copy up and running follow these simple steps.
* Dependencies
  ```sh
  pip install customtkinter
  ```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/SalemAitAmi/Secure-GUI-Chat.git
   ```
2. Enter the directory
   ```sh
   cd Secure-GUI-Chat
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

1. Start the server
   ```sh
   python server.py
   ```
2. Start clients through separate terminals
   ```sh
   python client.py
   ```
3. Login

[![Login Screen Shot][Login-screenshot]](https://github.com/SalemAitAmi/Secure-GUI-Chat/blob/main/assets/images/login.png)

### Sample Profiles

| Usename | Password |
|---------|----------|
| Alice   | alice    |
| Boby    | boby     |
| Ryan    | ryan     |
| Samy    | Samy     |
| Ted     | ted      |
| Admin   | admin    |

Use any of the above credentials to get past the login window, or register under your own username and password.

4. Register

[![Register Screen Shot][Registration-screenshot]](https://github.com/SalemAitAmi/Secure-GUI-Chat/blob/main/assets/images/register.png)

5. Chat Selection

[![Chat Selection Screen Shot][Selection-screenshot]](https://github.com/SalemAitAmi/Secure-GUI-Chat/blob/main/assets/images/selection.png)

6. Sample Chat

[![Chat Screen Shot][Chat-screenshot]](https://github.com/SalemAitAmi/Secure-GUI-Chat/blob/main/assets/images/chat-sample.png)

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTACT -->
## Contact

Salem Ait Ami - [LinkedIn](https://www.linkedin.com/in/salemaitami/) - [salemaitami@uvic.ca](salemaitami@uvic.ca)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[Login-screenshot]: assets/images/login.png
[Registration-screenshot]: assets/images/register.png
[Selection-screenshot]: assets/images/selection.png
[Chat-screenshot]: assets/images/chat-sample.png
