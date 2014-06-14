from SimpleMenu import Menu

newmenu = Menu("Yes", "No", title="hello!", subtitle="A very excellent menu")
choice = newmenu.show()
print(choice)