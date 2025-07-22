"""English translations of the program interface"""

MSG_WELCOME_1 = "Welcome to Calcuresu"
MSG_WELCOME_2 = "Your terminal task manager!"
MSG_WELCOME_3 = "Config and data files were created at:"
MSG_WELCOME_4 = "For support, contribution, and additional information, visit:"
MSG_WELCOME_5 = "Press ? to see all keybindings or any other key to continue."

TITLE_KEYS_GENERAL = "GENERAL KEYBINDINGS"
TITLE_KEYS_WORKSPACE = "WORKSPACE KEYBINDINGS"
TITLE_KEYS_ARCHIVE = "ARCHIVE KEYBINDINGS"
TITLE_KEYS_JOURNAL  = "JOURNAL KEYBINDINGS"

KEYS_GENERAL = {
        " Space ": "Switch between archive and journal",
        "   ?   ": "Toggle this help",
        "   Q   ": "Reload",
        "   q   ": "Quit",
        "  1-6  ": "Alternate between windows",
}

KEYS_ARCHIVE = {
        "   o   ": "View/Modify task's extra info",
        "   /   ": "Apply filter to archived tasks",
        "   x   ": "Restore to journal (supports children)",
        " PGDWN ": "Go 6 tasks down",
        " PGDUP ": "Go 6 tasks up",
        "   ↑   ": "Go 1 task up",
        "   ↓   ": "Go 1 task down",
}

KEYS_WORKSPACE = {
        "   a   ": "Add",
        "   l   ": "Load and go to journal",
        "   x   ": "Delete",
        " PGDWN ": "Go 6 workspaces down",
        " PGDUP ": "Go 6 workspaces up",
        "   ↑   ": "Go 1 workspace up",
        "   ↓   ": "Go 1 workspace down",
}

KEYS_JOURNAL = {
        " a(A)  ": "Add (sub)task",
        "   o   ": "View/Modify extra info",
        "   /   ": "Apply filter to journal tasks",
        "   x   ": "Delete/Archive (supports children)",
        "   X   ": "Delete/Archive all items",
        "   m   ": "Move (supports children)",
        "   e   ": "Exchange task locations",
        "   r   ": "Rename",
        "   c   ": "Collapse/Expand",
        "   i   ": "Modify importance",
        "   s   ": "Modify status",
        "   d   ": "Mark as done",
        "   .   ": "Toggle privacy mode",
        "  t(T) ": "Start/Stop/(reset) timer",
        "  f(F) ": "Apply/(reset) deadline",
        " PGDWN ": "Go 6 tasks down",
        " PGDUP ": "Go 6 tasks up",
        "   ↑   ": "Go 1 task up",
        "   ↓   ": "Go 1 task down",
}

MSG_NAME          = "CALCURE"
MSG_INFO          = "For more information, visit:"
MSG_SITE          = "https://github.com/guysudai1/calcuresu"
MSG_EXIT          = "Really exit? "

MSG_EVENT_HIGH    = "Mark as high priority event number: "
MSG_EVENT_LOW     = "Mark as low priority event number: "
MSG_EVENT_DONE    = "Mark as done event number: "
MSG_EVENT_RESET   = "Reset status for event number: "
MSG_EVENT_DEL     = "Delete event number: "
MSG_EVENT_REN     = "Rename event number: "
MSG_NEW_TITLE     = "Enter new title: "
MSG_EVENT_MV      = "Move event number: "
MSG_EVENT_MV_TO   = "Move event to (YYYY/MM/DD): "
MSG_EVENT_MV_TO_D = "Move event to: "
MSG_EVENT_DATE    = "Enter date: "
MSG_EVENT_TITLE   = "Enter title: "
MSG_EVENT_REP     = "How many times repeat the event: "
MSG_EVENT_FR      = "Repeat the event every (d)ay, (w)eek, (m)onth or (y)ear? "
MSG_EVENT_IMP     = "Import events from Calcurse?"
MSG_EVENT_PRIVACY = "Toggle privacy of event number: "
MSG_TM_ADD        = "Add/pause timer for task number: "
MSG_TM_RESET      = "Remove timer for the task number: "
MSG_TS_RENAME_TASK = "Rename task text: "
MSG_TS_INPUT_TASK = "Task content here... (Tip: use @ to display icons in the task)"
MSG_TS_NEW_TASK = "New task text: "
MSG_WS_NEW_WORKSPACE = "New workspace path: "
MSG_WS_NEW_WORKSPACE_TIP = "Workspace path here... (Tip: the lock file will be at <workspace_path>.lock)"
MSG_TS_EXTRA_INFO_TASK = "Mark task to modify/view its extra info: "
MSG_TS_COLLAPSE = "Mark task number to collapse/uncollapse: "
MSG_TS_IMPORTANCE = "Mark task number to change importance for: "
MSG_TS_STATUS = "Mark task number to change status for: "
MSG_TS_FILTER = "Select which field to filter: "
MSG_TS_FILTER_NAME = "Regex for filtering task name: "
MSG_TS_FILTER_EXTRA_INFO = "Regex for filtering task extra info: "
MSG_TS_FILTER_STATUS = "Display tasks with following status: "
MSG_TS_FILTER_IMPORTANCE = "Display tasks with following importance: "
MSG_TS_RES        = "Reset status for the task number: "
MSG_TS_DONE       = "Mark as done the task number: "
MSG_TS_RES        = "Restore task number: "
MSG_WS_LOAD        = "Load workspace number: "
MSG_TS_RES_ALL    = "Restore all tasks to journal?"
MSG_TS_DEL        = "Delete task number: "
MSG_TS_CHILDREN_DEL = "Delete all children too?"
MSG_TS_CHILDREN_ARCHIVE = "Archive all children too?"
MSG_TS_ARCHIVE = "Archive task number: "
MSG_TS_DEL_ALL    = "Really delete all tasks?"
MSG_TS_ARCHIVE_ALL    = "Really archive all tasks?"
MSG_WS_DEL        = "Delete workspace number: "
MSG_TS_EDT_ALL    = "Do you confirm this action?"
MSG_TS_MOVE       = "Move task from number: "
MSG_TS_MOVE_TO    = "Move task to number (0=root): "
MSG_TS_EDIT       = "Edit task number: "
MSG_TS_TOG        = "Toggle subtask number: "
MSG_TS_SUB        = "Add subtask for task number: "
MSG_TS_TITLE      = "Enter subtask: "
MSG_TS_IM         = "Import tasks from Calcurse?"
MSG_TS_TW         = "Import tasks from Taskwarrior?"
MSG_TS_NOTHING    = "Nothing planned..."
MSG_TS_NO_WORKSPACES    = "No workspaces found. Create a new one by clicking 'a'"
MSG_TS_PRIVACY    = "Toggle privacy of task number: "
MSG_TS_DEAD_ADD   = "Add deadline for task number: "
MSG_TS_DEAD_DEL   = "Remove deadline of the task number: "
MSG_TS_DEAD_DATE  = "Add deadline on (YYYY/MM/DD): "
MSG_WEATHER       = "Weather is loading..."
MSG_ERRORS        = "Errors have occurred. See info.log in your config folder."
MSG_INPUT         = "Incorrect input."
MSG_GOTO          = "Go to date (YYYY/MM/DD): "
MSG_GOTO_D        = "Go to date: "

JOURNAL_HINT      = "Space · Switch to archive   a · Add   d · Done   s · Status   i · Importance   / · Filter  ? · All keybindings"
ARCHIVE_HINT      = "Space · Switch to journal   x · Restore   o · Extra Info   / · Filter  ? · All keybindings"
WORKSPACE_HINT      = "a · Add   l · Load   x · Delete  ? · All keybindings"

DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
DAYS_PERSIAN = ["SHANBEH", "YEKSHANBEH", "DOSHANBEH", "SESHANBEH", "CHAHARSHANBEH", "PANJSHANBEH", "JOMEH"]

MONTHS = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
MONTHS_PERSIAN = ["FARVARDIN", "ORDIBEHESHT", "KHORDAD", "TIR", "MORDAD", "SHAHRIVAR", "MEHR", "ABAN", "AZAR", "DEY", "BAHMAN", "ESFAND"]
