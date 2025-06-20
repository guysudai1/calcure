"""English translations of the program interface"""

MSG_WELCOME_1 = "Welcome to Calcure"
MSG_WELCOME_2 = "Your terminal calendar and task manager!"
MSG_WELCOME_3 = "Config and data files were created at:"
MSG_WELCOME_4 = "For support, contribution, and additional information, visit:"
MSG_WELCOME_5 = "Press ? to see all keybindings or any other key to continue."

TITLE_KEYS_GENERAL = "GENERAL KEYBINDINGS"
TITLE_KEYS_CALENDAR = "CALENDAR KEYBINDINGS"
TITLE_KEYS_JOURNAL  = "JOURNAL KEYBINDINGS"

KEYS_GENERAL = {
        " Space ": "Switch between calendar and journal",
        "   /   ": "Toggle split screen",
        "   *   ": "Toggle global privacy",
        "   ?   ": "Toggle this help",
        "   Q   ": "Reload",
        "   q   ": "Quit",
        }

KEYS_CALENDAR = {
        "  a(A) ": "Add a (recurring) event",
        "   n   ": "Next month (day)",
        "   p   ": "Previous month (day)",
        "   x   ": "Delete an event",
        "   r   ": "Rename an event",
        "  m(M) ": "Move event (in this month)",
        "  g(G) ": "Go to a certain day (in this month)",
        "   v   ": "Toggle daily/monthly view",
        "   h   ": "Toggle event as high priority",
        "   l   ": "Toggle event as low priority",
        "   d   ": "Toggle event as done",
        "   .   ": "Toggle event privacy",
        "   C   ": "Import events from calcurse",
        "   R   ": "Return to current month (day)",
        }

KEYS_TODO = {
        "  a(A) ": "Add new (sub)task",
        "  h(H) ": "Toggle one (all) of the tasks as high priority",
        "  l(L) ": "Toggle one (all) of the tasks as low priority",
        "  d(D) ": "Toggle one (all) of the tasks as done",
        "  u(U) ": "Unmark one (all) of the tasks",
        "  x(X) ": "Delete one (all) of the tasks (with all subtasks)",
        "  t(T) ": "Start/pause (remove) timer for a task",
        "   r   ": "Rename a task",
        "   s   ": "Toggle between task and subtask",
        "   .   ": "Toggle task privacy",
        "  f(F) ": "Change (remove) task deadline",
        "   m   ": "Move a task",
        "   C   ": "Import tasks from calcurse",
        }

MSG_NAME          = "CALCURE"
MSG_VIM           = "Arrow and Vim keys (j, k, ZZ, ZQ) work as well!"
MSG_INFO          = "For more information, visit:"
MSG_SITE          = "https://anufrievroman.gitbook.io/calcure"
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
MSG_TS_DEL_ALL    = "Really delete all tasks?"
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

JOURNAL_HINT      = "Space · Switch to calendar   a · Add task   d · Done   i · Important   ? · All keybindings"
ARCHIVE_HINT      = "Space · Switch to calendar   a · Add task   d · Done   i · Important   ? · All keybindings"

DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
DAYS_PERSIAN = ["SHANBEH", "YEKSHANBEH", "DOSHANBEH", "SESHANBEH", "CHAHARSHANBEH", "PANJSHANBEH", "JOMEH"]

MONTHS = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
MONTHS_PERSIAN = ["FARVARDIN", "ORDIBEHESHT", "KHORDAD", "TIR", "MORDAD", "SHAHRIVAR", "MEHR", "ABAN", "AZAR", "DEY", "BAHMAN", "ESFAND"]
