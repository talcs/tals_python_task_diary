# Tal's Python Task Diary

**Tal's Python Task Diary** is a simple & light Python graphical application, built for setting, tracking and managing tasks.

## Prerequisites

The only dependency for **Tal's Python Task Diary** is Python. The used **Tk** GUI libraries are available in the basic Python distribution.

The project was tested only with Python **3.5.1**. It may work on any **Python 3.x** version that was released with **Tcl8.6 or higher** (a rough guess is that if you use a version that was released in 2014 or later, there should not be a problem)


## Features

  * Manage tasks in an hierarchical structure
  * Specify task's priority, completion percent, category
  * Specify sub-tasks weight in percents, in terms of its parent task


## Screenshots

![alt text](https://s23.postimg.org/xn221ri8b/td_sc.png Screenshot)


## Things You Need to Know as a User

  * Your tasks are saved locally on your machine, in **&lt;USER_HOME_DIR&gt;/tals_python_task_diary_data.xml**  . It is more than recommended to backup this file occasionally !!! (You don't want to lose all the tasks and their statuses because of some silly mistake or problem)
  * Be careful not to run multiple instances of the tasks diary at the same time for the same user, as your data will be overriden each time you perform any action in any of the instances
  * This project was briefly written for fun and for my own needs. You can improve it if you like. Anyway, the usage is on your own risk and responsibility

