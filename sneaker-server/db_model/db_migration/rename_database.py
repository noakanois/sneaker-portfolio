import os
import logging

if not os.path.exists("../../shoes.db"):
    os.rename("../../test.db", "../../shoes.db")