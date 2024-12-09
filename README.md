# Datamaster Development Standards

This repository provides a reusable template for implementing **GitHub Actions workflows** and **commit message validation** to enforce development standards across all Datamaster repositories. The goal is to ensure consistency, quality, and efficiency in our projects.

---

## 🚀 Features

### 1. **GitHub Actions Workflows** 🛠️
- 🔄 **Automates CI/CD pipelines** for faster and more reliable builds.
- 📝 **Commit message validation workflow** ensures compliance with [Conventional Commits](https://www.conventionalcommits.org/), promoting clean and consistent commit history.
- 🔍 Validates changes in **GitHub Actions workflows** automatically within pull requests, ensuring smooth integration.

### 2. **Commit Message Validation** 📜
- 📏 Enforces a **structured format** for commit messages to improve readability and consistency:
  - **type**: Describes the *nature* of the change (e.g., `feat`, `fix`, `chore`, `docs`).
  - **scope**: *Optional*; provides *context* for the change (e.g., `api`, `auth`).
  - **short description**: A *concise description* of the change, keeping it clear and to the point.

### 3. **Reusability** 🔄
- 🛠️ **Easily integrates** into any repository in just a few steps.
- ⚙️ **Highly customizable** to suit your project's unique needs, making it adaptable for a wide range of use cases.

## 🛠️ Installation and Usage

### **Prerequisites** ⚙️
Before you begin, make sure you have the following:
- **Git** initialized in your repository.
- **Admin** or **write** access to the repository to make necessary changes.

---

### **Steps to Use This Template** 🚀

1. **Clone the Template Repository** 🖥️
   
   First, clone the repository to your local machine:
   ```bash
   git clone https://github.com/datamaster-team/datamaster-dev-standards.git
   cd datamaster-dev-standards
    ```
2. **Run the Setup Script** 🎬

    Use the provided **setup script** to integrate the template into your repository automatically. This will configure everything needed to get started without manual intervention. Here's how:

    In your terminal, run the following command:
    ```bash
    ./scripts/setup.sh
    ```

<!-- 
### **Manual Setup** 🛠️

If you prefer **manual integration**, follow the steps below to integrate the Datamaster development standards into your repository.

---

#### **1. Copy the `.github` Folder 📁**

First, you need to copy the `.github` folder from this repository into your own project. This folder contains the necessary GitHub Actions workflows to automate your CI/CD process and commit message validation.

**Steps:**

1. Copy the `.github` folder to your repository:
   ```bash
   cp -r .github /path/to/your/repo/
    ```

#### **2. Integrate Git Hooks 🔑**

Git hooks are scripts that run automatically at certain points during the Git workflow. By integrating the `commit-msg` hook, you ensure that every commit message follows the required format before being committed to the repository.

**Steps to integrate Git hooks:**

1. **Copy the `commit-msg` hook** from this repository to your local `.git/hooks` directory:
   ```bash
   cp hooks/commit-msg .git/hooks/

2. **Make the hook executable by running the following command:**   
    ```bash
    chmod +x .git/hooks/commit-msg
    ```
3. **Commit a change to test if the hook is working:**
    ```bash
    git commit -m "feat(auth): add user authentication
    Refs: #CU-8695gk8c7"
    ``` -->

### **Commit and Push Changes 🚀**

After setting up the repository (either manually or using the setup script), it's time to commit your changes and push them to your remote repository.

1. **Commit Message Guidelines**

    Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

    #### **Example:**

    ```bash
    feat(auth): add login feature

    Added the ability for users to log in using their email and password.

    Refs: #CU-8695gk8c7
    ```

2. **Steps to commit and push changes:**

    1. **Stage the changes 📥**

        Make sure all the changes are added to the staging area before committing.
        ```bash
        git add .
        ```
    2. **Commit your changes ✍️**

        Write a meaningful commit message that follows the [Conventional Commits](https://www.conventionalcommits.org/) format.
        ```bash
        git commit -m "chore: integrate Datamaster standards template"
        ```
    3. **Push the changes to your repository 🌐**

        Finally, push the changes to the remote repository:
        ```bash
        git push origin <branch-name>
        ```
    *Note: Replace <branch-name> with the name of your current branch (e.g., main, feature/xyz).*


## **Valid Commit Types ✅**

Commit messages follow specific types to maintain clarity and consistency in the repository. Each commit type represents a different category of change, making it easier to understand the purpose of a commit at a glance.

### **Here are the valid commit types:**

| **Type**    | **Description**                                                                 |
|-------------|---------------------------------------------------------------------------------|
| **`feat`**  | ✨ _A new feature_ for the application or service.                             |
| **`fix`**   | 🐞 _A bug fix_ that addresses an issue in the application or service.         |
| **`docs`**  | 📚 _Documentation changes_—anything related to updating or improving docs.    |
| **`style`** | 💅 _Code style changes_ such as formatting or cosmetic updates (no functional changes). |
| **`refactor`** | 🔄 _Refactoring code_—modifying the structure of the code without changing its functionality. |
| **`test`**  | 🧪 _Adding or updating tests_ to improve test coverage or fix broken tests.   |
| **`chore`** | 🛠 _Maintenance tasks_ or changes to build processes or dependencies.          |
| **`perf`**  | ⚡ _Performance improvements_ that make the app or service faster or more efficient. |
| **`ci`**    | 🔧 _Changes to CI configuration files_ or related scripts.                    |
| **`build`** | 🏗 _Changes affecting the build system_ or dependencies that affect the build. |

---

> **Tip:** Choose the commit type carefully! A well-structured commit message will help you and your team maintain clean, understandable version history. 💡

***By using these commit types, we ensure our project remains easy to navigate, and our version history is both organized and clear.***





## **Local Validation with Git Hooks 🛠️**

Git hooks are a great way to ensure that your commit messages follow the required format **before** they even get committed. This guarantees that all commit messages are validated locally, maintaining consistency across all commits!

### **Here’s how to set it up:**

1. **Copy the `hooks scripts` to Your `.git/hooks` Directory 🔄**

   First, you need to copy the `hooks scripts` into your repository’s `.git/hooks` directory. This will automatically trigger the validation on commit creation.

   ```bash
   cp hooks/* .git/hooks/
   chmod +x .git/hooks/*
   ```

2. **Test the Hook by Making a Commit 📝**

    Now that you've set up the commit message validation hook, it's time to **test** if everything is working as expected! 💡

    #### **Steps:**

    1. **Make a Commit with a Message 📌**

        Try making a commit using the command below. Use a message that follows the **Conventional Commits** format:

        ```bash
        git commit -m "feat(UI): implement user login page
        Refs: #CU-8695gk8c7"
        ```   
    




## 🛠️ **GitHub Actions Workflows** ⚙️

When you commit and push changes to your repository, **GitHub Actions** automatically kicks in to ensure everything is in order. This includes validating your commit messages, pull request titles, and even generating changelogs when a new release is created. 🎉

---

### **How it Works:**

#### **Commit Message Validation 🚦**
Once you commit and push your changes to the repository, a **GitHub Actions workflow** is triggered to validate your commit message. It checks whether your commit message follows the prescribed **Conventional Commits** format.

- If your message is valid, the workflow passes, and your changes are accepted.
- If your message does not follow the correct format, the workflow fails, and you'll be asked to update your commit message.

#### **Pull Request Title Validation 📝**
In addition to commit message validation, the workflow also validates **pull request titles**. It ensures that pull request titles follow the same **Conventional Commits** format, maintaining uniformity across all pull requests.

- If your PR title is valid, the workflow proceeds smoothly.
- If it doesn’t conform to the format, you’ll be prompted to adjust it before merging.

#### **Changelog Generation 📋**
When a **new release** is created with a **tag** that follows the format `v*.*.*` (for example, `v1.0.0`), GitHub Actions automatically triggers a workflow to generate the **changelog**. This process compiles all the relevant changes from commits and pull requests into a structured changelog, making it easier to track new features, bug fixes, and other updates.

- After generating the changelog, an automatic email is sent to notify you about the successful changelog generation, ensuring that your team stays informed about the latest changes.

---

### **Why This Matters 💡**

By **automating commit message validation**, **pull request title validation**, and **changelog generation**, you gain the following benefits:

- 🔄 **Consistency in Commit History**  
  Ensures a clean and consistent commit log, making it easier to understand project progress and track changes across versions.

- ⏱️ **Time-saving Automation**  
  With automated checks in place, you eliminate the risk of human error, saving valuable time and ensuring that every commit message and PR title follow the required format.

- ✅ **Quality Control**  
  Helps maintain high standards and avoids messy commit histories, which improves collaboration and code readability across teams.

- 📝 **Automated Changelog Generation**  
  Automatically compiles and generates a changelog with each new release (tagged `v*.*.*`), along with an email notification sent after every successful changelog update, helping your team stay informed without additional manual work.

This small step leads to a **big impact** on the maintainability and professionalism of your codebase! 🚀


## 🗂️ **Project Structure** 📁

The repository is organized to ensure a smooth workflow and easy integration of the template. Below is an overview of the key directories and files:

---

### **1. `.github/`** 🔧
- **What it is**: Contains shared GitHub Actions workflows that will be integrated into all other repositories.
- **Purpose**: Automates CI/CD tasks, including validating commit messages and managing other continuous integration processes.

### **2. `repoName/`** 🔑
- **What it is**: Represents the individual repository structure.
  - **`scope`**: A script for specific scopes relevant to this repository.
  - **`.github/`**: Contains repository-specific GitHub Actions workflows.
  - **`hooks/`**: Holds Git hooks to enforce commit message standards locally.
- **Purpose**: Each repository follows this structure to maintain consistency and smooth integration with the shared templates.

### **3. `scripts/setup.sh`** ⚙️
- **What it is**: A shell script to automate the setup process of the commit message standards and other integrations.
- **Purpose**: Helps in setting up the commit standards locally, ensuring uniformity across all repositories.

### **4. `README.md`** 📚
- **What it is**: This file!
- **Purpose**: Provides an overview of how to use the repository template and detailed instructions on setting up and configuring the repository.

---

This structure simplifies management and ensures consistent integration across multiple repositories, with shared workflows and hooks for effective version control and commit validation.

## Contributing 🤝

We welcome **contributions** to improve this template and help us build a better developer experience for everyone!

Here’s how you can get involved:

1. **Fork the Repository**  
   First, click on the **Fork** button at the top-right of this page to create your own copy of this repository.

2. **Create a New Branch**  
   After forking, clone your repository and create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Your Changes ✨**

    Now that you've set up your local environment, it's time to get your hands dirty and make those awesome changes! 🚀

    ### Here’s how you can proceed:

    1. **Identify the Task**  
    Before diving in, make sure you know what you're working on. Whether it’s a new feature, a bug fix, or an improvement, having a clear goal will make your development smoother.

    2. **Write Clean Code**  
    Follow the project’s coding standards and write code that is easy to read and maintain. Think about others who will be reading your code!

    3. **Test Locally**  
    After making your changes, test them **locally** to ensure everything works as expected. You don’t want to push untested code to the main branch!

    4. **Ensure Compatibility**  
    Make sure your changes don’t break existing functionality. Run the project’s tests (or create new ones) to confirm everything stays in check.

    5. **Follow Commit Message Guidelines**  
    Don’t forget to craft a meaningful commit message that follows the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) format. This ensures that your commits are clear and structured.

    With your changes ready, you’re all set to **commit** and **push** them to your branch and move to the next step! 🎉


4. **Submit a Pull Request 🏁**

    Ready to share your amazing changes with the world? Now’s the time to submit your **pull request (PR)**! Here’s how to do it smoothly and efficiently:

    **Steps:**

    1. **Push Your Changes**  
    Make sure your changes are pushed to your branch. If you haven’t done that yet, follow these steps:
    ```bash
    git push origin <branch-name>
    ```
5. **Open a New Pull Request 🔄**

    Once you’ve committed and pushed your changes, it’s time to open a **pull request** (PR) to propose your changes to the main codebase. Let’s get started:

    **Steps to Open a PR:**

    1. **Go to Your GitHub Repository**  
    Navigate to the repository where you’ve made changes. Make sure you’re on the branch you want to submit.

    2. **Click the "New Pull Request" Button**  
    On the GitHub repository page, locate the **"Pull requests"** tab at the top, then click **"New Pull Request"**.

    3. **Select the Branch to Compare**  
    GitHub will prompt you to select the branch you want to compare. Select your feature branch (the one with your changes) and the base branch (usually `main` or `develop`).

    4. **Review the Changes**  
    GitHub will show a diff of the changes you’ve made. Take a moment to review them, ensuring everything is correct.

    5. **Add a Meaningful Title and Description**  
    - **Title**: Write a concise summary of what your PR does. (e.g., "feat(auth): add login functionality")
    - **Description**: Provide additional context about the changes made, why they’re necessary, and any related issues or references.

    6. **Example:**
    
        **Title:**
        feat(auth): add login functionality

        **Description:**
        This PR introduces email/password authentication for users and implements session management.

        **Related Issues:**
        Refs: #234
    
## Maintainers 👩‍💻👨‍💻

This repository is maintained by the ***Datamaster Team***. Our goal is to keep this template up to date, and we welcome any feedback or contributions from the community.

If you encounter issues, have questions, or would like to suggest improvements, please don’t hesitate to open an issue or reach out to us!

### Contact Us:
- **Email**: support@datamaster.com
- **GitHub Issues**: [Open an Issue](https://github.com/datamaster-team/datamaster-dev-standards/issues)


We’re here to help! 💬


## License 📝

This repository is licensed under the **MIT License**.

You are free to:

- **Use**: Utilize this template in your projects.
- **Modify**: Make changes and improvements to suit your needs.
- **Distribute**: Share this template with others.

However, please note that the software is provided "as is," without warranty of any kind.
