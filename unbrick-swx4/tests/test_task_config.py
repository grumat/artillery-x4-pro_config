#
# -*- coding: UTF-8 -*-
#
# Spellchecker: words USWX

import os
import sys
from typing import TYPE_CHECKING

# Enable test environment
os.environ["USWX4_TEST"] = "test_task_config"


# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the 'assets' directory
project_dir = os.path.normpath(os.path.join(current_dir, '..'))

# Add the 'project_dir' directory to sys.path
sys.path.append(project_dir)

#from my_env import Info
if TYPE_CHECKING:
	from ..user_options import UserOptions
	from ..my_workflow import Workflow
else:
	from user_options import UserOptions
	from my_workflow import Workflow


def main():
	opts = UserOptions()
	opts.printer = 1	# Artillery plus will conflict with default used in test
	wf = Workflow(opts)
	wf.Test()


if __name__ == "__main__":
	main()
