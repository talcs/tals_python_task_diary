from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import Tk
import xml.etree.ElementTree as ET
import os

tree = None
tree_context_menu = None
root_context_menu = None

TITLE_TEXT = 'Tal\'s Python Task Diary'
DEFAULT_NEW_SUBTASK_NAME = 'New Sub Task'
DEFAULT_XML_FILE = os.path.join(os.path.expanduser('~'), 'tals_python_task_diary_data.xml')

ROOT_TASK_DEFAULT_VALS = ('Medium', '0%', '', 'General')
SUB_TASK_DEFAULT_VALS = ('', '0%', '0%', '')


def string_to_clipboard(str_val):
	r = Tk()
	r.withdraw()
	r.clipboard_clear()
	r.clipboard_append(str_val)
	r.destroy()

def insert_data_to_tree(tree, data, parent_item_id = None):
	for dataitem in data:		
		node_id = tree.insert('' if parent_item_id == None else parent_item_id, 'end', '',text = dataitem['values'][0], values = tuple(dataitem['values'][1:]))
		if 'children' in dataitem:
			insert_data_to_tree(tree, dataitem['children'], node_id)
		
def create_tree(parent, data):
	scrollbar = ttk.Scrollbar(mainframe)
	tree = ttk.Treeview(mainframe)
	scrollbar.config(command=tree.yview)
	scrollbar.grid(column=3, row=1, sticky=(N,S))
	tree.config(yscrollcommand=scrollbar.set)
	tree['columns'] = ('Priority', 'Completeness', 'Weight in Task', 'Group')
	tree.heading('#0', text='Task Name')
	for colname in tree['columns']:
		tree.column(colname, anchor='center')
		tree.heading(colname, text=colname)
	tree.grid(column=2, row=1, sticky=(W, E))
	insert_data_to_tree(tree, data)
	
	return tree

def xml_task_to_data_structure(node):
	item = {}
	item['values'] = [node.attrib['Text'], node.attrib['Priority'], node.attrib['Completeness'], node.attrib['WeightInTask'], node.attrib['Group']]
	item['children'] = []
	for child in node: # Children Tag
		for real_child in child:
			item['children'].append(xml_task_to_data_structure(real_child))
	
	return item
	
def read_tree_data_from_xml(xml_file):
	if not os.path.isfile(xml_file):
		return []
	xml = ET.parse(xml_file)
	xml_root = xml.getroot()
	if xml_root.tag != 'TaskDiaryTasklist':
		pass
		# Error
	tasks = []
	for main_task in xml_root:
		tasks.append(xml_task_to_data_structure(main_task))
	
	return tasks
	
def get_data():
	item1 = {}
	item1['values'] = ['task 1', 'high', '35%', '', 'thesis']
	item1_1 = {}
	item1_2 = {}
	item1['children'] = [item1_1, item1_2]
	item1_1['values'] = ['subtask1', '', '66%', '50%', '']
	item1_2['values'] = ['subtask2', '', '16%', '50%','']
	item1_1_1 = {}
	item1_1_1['values'] = ['subsubtask1', '', '66%', '100%', '']
	item1_1['children'] = [item1_1_1]
	item2 = {}
	item2['values'] = ['task 2', 'high', '10%', '', 'studies']
	
	return [item1, item2]
	
def tree_to_xml(tree_root, xml_parent = None, tree_parent_item_id = None):
	if xml_parent == None:
		xml_parent = ET.Element('TaskDiaryTasklist')
		children = tree_root.get_children()
	else:
		children = tree_root.get_children(tree_parent_item_id)
	for child_id in children:
		child_obj = tree_root.item(child_id)
		xml_child = ET.SubElement(xml_parent, 'TaskDiaryTask')
		xml_child.set('Text', str(child_obj['text']))
		obj_values = tuple(child_obj['values'])		
		xml_child.set('Priority', str(obj_values[0]))
		xml_child.set('Completeness', str(obj_values[1]))
		xml_child.set('WeightInTask', str(obj_values[2]))
		xml_child.set('Group', str(obj_values[3]))
		xml_child_children_node = ET.SubElement(xml_child, 'Children')
		tree_to_xml(tree_root, xml_child_children_node, child_id)
	
	return xml_parent

def update_tree_value(row, col, value):
	row_item_id = row
	item_obj = tree.item(row_item_id)
	item_txt = str(item_obj['text'])
	item_vals = list(item_obj['values'])
	if col == 0:
		item_txt = value
	else:
		item_vals[col - 1] = value
	tree.item(row_item_id, text = item_txt, values = tuple(item_vals))

def get_tree_value(row, col):
	row_item_id = row
	item_obj = tree.item(row_item_id)
	if col == 0:
		return str(item_obj['text'])
	item_vals = tuple(item_obj['values'])

	return str(item_vals[col - 1])
	
def popup_context_menu(event):
	global popup_row_id
	global popup_col_id
	popup_row_id = tree.identify_row(event.y)
	sel = tree.selection()
	if len(sel) > 1:
		# For cases of multiple selected items, we only allow deletion, and only if mouse was on one of selected items
		if popup_row_id not in sel:
			return
		tree_context_menu_multiple_selection.post(event.x_root, event.y_root)
		return	
	if not (popup_row_id == '' or (len(sel) > 0 and sel[0] == popup_row_id)):
		return
	popup_col_id = tree.identify_column(event.x)
	popup_col_id = None if popup_col_id == '' else int(popup_col_id[1:])
	if popup_col_id == '' or popup_row_id == '':
		root_context_menu.post(event.x_root, event.y_root)
		return
	has_next_sibling = tree.next(popup_row_id) != ''
	has_prev_sibling = tree.prev(popup_row_id) != ''
	if has_next_sibling and has_prev_sibling:
		tree_context_menu_both_neighbors.post(event.x_root, event.y_root)
	elif has_next_sibling:
		tree_context_menu_lower_neighbor.post(event.x_root, event.y_root)
	elif has_prev_sibling:
		tree_context_menu_upper_neighbor.post(event.x_root, event.y_root)
	else:
		tree_context_menu_no_neighbors.post(event.x_root, event.y_root)  

def prompt_change_cell_value():
	val = simpledialog.askstring('Edit...', 'Please enter new value', initialvalue = get_tree_value(popup_row_id, popup_col_id))
	if val == None:
		return
	update_tree_value(popup_row_id, popup_col_id, val)
	save_tree_to_xml(tree, DEFAULT_XML_FILE)
	
def prompt_delete_row():
	ans = messagebox.askquestion("Delete Task / Sub Task", "This task and all its sub tasks will be deleted. This action is not reversible! Are You Sure?", icon='warning')
	if ans != 'yes':
		return
	tree.delete(popup_row_id)
	save_tree_to_xml(tree, DEFAULT_XML_FILE)

def add_new_sub_item():
	containing_row_id = popup_row_id
	vals = SUB_TASK_DEFAULT_VALS if containing_row_id != '' else ROOT_TASK_DEFAULT_VALS
	tree.insert(containing_row_id, 'end', '',text = DEFAULT_NEW_SUBTASK_NAME, values = vals)
	save_tree_to_xml(tree, DEFAULT_XML_FILE)
	
def move_row_up()	:
	containing_row_id = popup_row_id
	curr_index = tree.index(containing_row_id)
	tree.move(containing_row_id, tree.parent(containing_row_id), curr_index - 1)
	save_tree_to_xml(tree, DEFAULT_XML_FILE)

def move_row_down():
	containing_row_id = popup_row_id
	curr_index = tree.index(containing_row_id)
	tree.move(containing_row_id, tree.parent(containing_row_id), curr_index + 1)
	save_tree_to_xml(tree, DEFAULT_XML_FILE)

def add_new_sibling_item_above():
	containing_row_id = popup_row_id
	curr_index = tree.index(containing_row_id)
	parent_row_id = tree.parent(containing_row_id)
	vals = SUB_TASK_DEFAULT_VALS if parent_row_id != '' else ROOT_TASK_DEFAULT_VALS
	tree.insert(parent_row_id, curr_index, '',text = DEFAULT_NEW_SUBTASK_NAME, values = vals)
	save_tree_to_xml(tree, DEFAULT_XML_FILE)

def add_new_sibling_item_below():
	containing_row_id = popup_row_id
	curr_index = tree.index(containing_row_id)
	parent_row_id = tree.parent(containing_row_id)
	vals = SUB_TASK_DEFAULT_VALS if parent_row_id != '' else ROOT_TASK_DEFAULT_VALS
	tree.insert(parent_row_id, curr_index + 1, '',text = DEFAULT_NEW_SUBTASK_NAME, values = vals)
	save_tree_to_xml(tree, DEFAULT_XML_FILE)
	
def prompt_delete_multiple_selected_items():
	ans = messagebox.askquestion("Delete Multiple Tasks / Sub Tasks", "All the selected tasks and all their sub tasks will be deleted. This action is not reversible! Are You Sure?", icon='warning')
	if ans != 'yes':
		return
	tree.delete(*list(tree.selection()))
	
def create_context_menu(tree):
	menu = Menu(root, tearoff=0)
	menu.add_command(label="Edit...", command = prompt_change_cell_value)
	menu.add_command(label="New Sub Item...", command = add_new_sub_item)
	menu.add_command(label="New Sibling Item Above...", command = add_new_sibling_item_above)
	menu.add_command(label="New Sibling Item Below...", command = add_new_sibling_item_below)
	menu.add_separator()
	menu.add_command(label="Delete Task / Sub Task", command = prompt_delete_row)
	menu.add_separator()
	menu.add_command(label="Copy text to clipboard", command = copy_cell_value_to_clipboard)
	
	
	return menu

def copy_cell_value_to_clipboard():
	string_to_clipboard(get_tree_value(popup_row_id, popup_col_id))
	
def create_context_menu_no_neighbors(tree):
	return create_context_menu(tree)
	
def create_context_menu_upper_neighbor(tree):
	menu = create_context_menu(tree)
	menu.add_separator()
	menu.add_command(label="Move Up", command = move_row_up)

	return menu
	
def create_context_menu_lower_neighbor(tree):
	menu = create_context_menu(tree)
	menu.add_separator()
	menu.add_command(label="Move Down", command = move_row_down)

	return menu
	
def create_context_menu_both_neighbors(tree):
	menu = create_context_menu(tree)
	menu.add_separator()
	menu.add_command(label="Move Up", command = move_row_up)
	menu.add_command(label="Move Down", command = move_row_down)
	
	return menu
	
def create_root_context_menu(tree):
	menu = Menu(root, tearoff=0)
	menu.add_command(label="New Item...", command = add_new_sub_item)
	
	return menu
	
def create_context_menu_multiple_selection(tree):
	menu = Menu(root, tearoff=0)
	menu.add_command(label="Delete all selected items...", command = prompt_delete_multiple_selected_items)
	
	return menu
	
def save_tree_to_xml(tree, xml_file):
	xml = ET.ElementTree(tree_to_xml(tree))
	xml.write(xml_file)
	
data = read_tree_data_from_xml(DEFAULT_XML_FILE)

root = Tk()
root.title(TITLE_TEXT)

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
tree = create_tree(mainframe, data)
tree.bind("<Button-3>", popup_context_menu)
tree_context_menu_no_neighbors = create_context_menu_no_neighbors(tree)
tree_context_menu_both_neighbors = create_context_menu_both_neighbors(tree)
tree_context_menu_lower_neighbor = create_context_menu_lower_neighbor(tree)
tree_context_menu_upper_neighbor = create_context_menu_upper_neighbor(tree)
tree_context_menu_multiple_selection = create_context_menu_multiple_selection(tree)
root_context_menu = create_root_context_menu(tree)

root.mainloop()

