from user import constants as user_constants
from company import constants as company_constants
from transporter import constatnts as consignment_constants
from disposal_agency import constants as disposal_constants
from company import company_status_constants as company_status_constants

user_constants = user_constants  # to avoid import warnings
company_constants = company_constants
consignment_constants = consignment_constants
disposal_constants = disposal_constants
company_status_constants = company_status_constants

read_actions = ['retrieve', 'list']
update_actions = ['update', 'partial_update']
create_actions = ['create']
delete_actions = ['destroy']
write_actions = update_actions + read_actions + update_actions + delete_actions
