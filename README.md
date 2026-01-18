# EcoWardrobe: A Clothing Library Platform

**Author:** Adrien Currat  
**Institution:** University of Lausanne, Msc. in Economics  
**Course:** Advanced Programming

## Introduction
EcoWardrobe is a Graphical User Interface (GUI) application developed using Python's Tkinter and a SQLite database. It simulates a digital clothing library where users can browse inventory, rent and return items, and report loss/damage. The app also includes a statistics dashboard and an “Eco-Comparator” that visualizes estimated CO₂ and water savings from renting instead of buying, supporting a circular-economy use case.

## Overview
This project combines basic Python programming concepts with advanced techniques to develop a user-friendly clothing library application.

- Core Python constructs such as **branching**, **loops**, **functions**, and **lists** are extensively used throughout the code. Two global lists facilitate the passing of information about items between different classes.
- A **SQLite database** of 500 clothing items is created to store detailed information about the clothing inventory, rentals, and returns.
- **Object-Oriented Programming (OOP)** is central to the project’s structure, ensuring the code is organised and easy to maintain. Several classes are defined, each responsible for a distinct part of the application. **Encapsulation** groups related data and methods within these classes, making the code more cohesive and manageable. **Inheritance** allows classes to reuse code from parent classes, promoting consistency across the application.
- **Matplotlib** is used to generate descriptive statistics and visual charts embedded directly into the application. 

## Content of the folder
Clothing_Library.py : This is the main Python script used to run the EcoWardrobe application. It contains all the necessary code to start the GUI, manage rentals and returns, and interact with the SQLite database.

Images Folder: This folder contains all the images used in the application. Ensure you update the file paths for the images in the application to match the paths on your local system



