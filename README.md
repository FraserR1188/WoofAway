# WoofAway

## Milestone Project 4 - Full Stack Frameworks with Django

- WoofAway is a full-stack Django web application designed to connect dog owners with verified, dog-friendly accommodation providers. The platform allows users to search, book, and review stays that cater specifically to their pets’ needs. At the same time, hosts can register and list their own dog-welcoming properties, manage bookings, and engage with guest feedback.

- The website offers a secure authentication system, a relational database with CRUD functionality for listings and bookings, and e-commerce integration via Stripe to process payments. With a clear user-focused interface, WoofAway aims to deliver a seamless, pet-conscious travel experience while demonstrating strong full-stack development practices in line with professional web application standards.

- This is my Milestoine Project 4 submission for Code Institutes Diploma in Web Application Development Course.

## Project Link

To access my website please click this [link]()

## Repository

To access my repository please click this [link](https://github.com/FraserR1188/WoofAway)

## Project Goals

The primary goal of WoofAway is to create a user-friendly, full-stack Django web application that meets the practical needs of dog owners seeking pet-friendly accommodation, while also providing a streamlined way for hosts to list and manage their properties.

# Table of Contents

## Contents

- [User Stories]

## User Stories

### Guest / Logged-in user (Customer looking to book)

- As a guest / logged-in user, I want to be able to register and log in so I can book listings and leave reviews.
- As a guest / logged-in user, I want to be able to search and filter listings so I can find suitable places for me and my dog.
- As a guest / logged-in user, I want to be able to view detailed listing pages so I can see pet-friendly features, photos and price.
- As a guest / logged-in user, I want to be able to make a secure booking so I can reserve a place for my trip.
- As a guest / logged-in user, I want to be able to pay for my trip easily.
- As a guest / logged-in user, I want to be able to recieve a booking confirmation so I know my booking is successful.
- As a guest / logged-in user, I want to be able to cancel a booking in case I change my mind.
- As a guest / logged-in user, I want to be able to leave a review so I can share my experiences with others.
- As a guest / logged-in user, I want to be able to view my bookings dashboard so I can keep track of my trips.
- As a guest / logged-in user, I want to be able to edit my account info in case they change for any reason.

### Host (Dog-friendly property owner)

- As a host, I want to register for a host account so I can list my dog-friendly accomomdation.
- As a host, I want to create a new listing so I can offer my home for bookings
- As a host, I want to edit or delete my listing so I can keep my information up-to-date
- As a host, I want to view bookings for my listing so I can manage who is staying at my place
- As a host, I want to prevent overlapping bookings so my property isn’t double-booked
- As a host, I want to respond to guest reviews so I can engage with guest feedback

### Webiste Owner (Admin of the platform)

- As a website owner, I want to access the Django admin panel so I can manage users, listings, and reviews
- As a website owner, I want to remove inappropriate listings or reviews so I can maintain platform safety and quality
- As a website owner, I want to view site-wide statistics or data so I can monitor usage or improve performance

## Design

### Overview

I want the design of the website to super easy to read and navigate. Simplistic design with smooth edges is what I have in mind. The name "WoofAway" implies what the website wants to achieve. It's clean, friendsly and repsonsive design inspired by Airbnb which is tailored for dog owners and hosts. The fonts which are select show a qurky yet understandable and legible.

### Colour

![Colour Scheme](docs/README/Colour%20palette.png)

### Typography

The fonts which I have picked are the playful Caveat for headings, logos and testimonials and the modern Quicksand font for body text, nav and buttons. Caveat adds a more personal feel and friendly feel and Quicksand is clear and easliy read.

### Imagery

The images which will be present on the website will be the logo for WoofAway and the pictures of the houses on the listings. The host will be able to upload them. A profile picture of the host can aslo be uploaded but not necessary.

### Icons

I used the Font Awesome icons for the social links which are present throughout the website in the footer.

### Wireframes

Mobile Wireframe

![Mobile Wireframe](docs/README/Wireframes/Mobile%20View.png)

Tablet Wireframe

![Tablet Wireframe](docs/README/Wireframes/iPad%20View.png)

Desktop Wireframe

![Desktop Wireframe](docs/README/Wireframes/Desktop%20View.png)

# Features

## Home Page

### Navigation Bar

![Navigation Bar Normal](docs/README/nav-bar-not-logged-in.png)

- This is what the navigation bar looks like when no one is logged in.

![Navigation Bar logged in as normal user](docs/README/nav-bar-logged-in-normal.png)

- This is the nav bar when a user is logged in.

![Navigation Bar user dropdown](docs/README/nav-bar-logged-in-dropdown.png)

- This the nav bar when the host or a normal user uses the dropdown menu to select their profile of bookings.

![Navigation Bar mobile](docs/README/nav-bar-mobile.png)

![Navigation Bar mobile dropdown](docs/README/nav-bar-mobile-user-options.png)

- This is the nav bar in a mobile view one when nothing is selected and the other when the burger menu has been touch.

![Navigation Bar mobile host](docs/README/nav-bar-mobile-host.png)

- This is the host view on the mobile view.

![Hero image home page](docs/README/hero-image-main-page.png)

- This is the hero image on the home page.

![Home page buttons](docs/README/homepage-buttons.png)

- These are home page buttons which take the user to the listings page or if they have an account/host then they can create a listing. The BROWSE LISTING button has been highlighted to show the animation effect.

![Main sections on home page](docs/README/section-with-main-headings.png)

- These are the main section headings on the home page which give good reason to choose this service. All links take the user to the section of the website intended.

![Footer](docs/README/footer.png)

- This is the footer which is present throughout the website. It contains a button which take the user to sign-up page if not already signed up. there also Font Awesome icons taking the user to the correct social media outlets.

## Sign Up Page

- I've test data in the screenshot to show how it looks.

![Test Login](docs/README/test-sign-up.png)

- This is the process how someone would sign up to the website.
- After the user has input the information, they then recieve an email into the inbox.

![Test Verification](docs/README/sign-up-verification.png)

- The email in the users inbox should look something like this.

![Test Inbox](docs/README/sign-up-inbox.png)

- Once the user has clicked on the link it should transport them back to the site to confirm.

![Test Confirm](docs/README/sign-up-confirm.png)

- Once confirmed, the user is then taken the login page to them start exploring the site with a user account.

## Login Page

![Login Page](docs/README/login.png)

## Profile
