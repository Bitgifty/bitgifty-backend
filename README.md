### Background ###
Performing an action is done by calling multiple functions,
as such, we would be using a bottom up approaching, starting
from the smallest funtion units and working our way up to
the final function call

### Instructions for swap ###

Swapping between currencies starts at the `wallets` module,
the `models.py` file contains two methods for taking and
placing funds into a wallet, this methods are the
`deduct` and `deposit` respectively and they can be found
in the `models.py` file of the wallets module.

Moving up one level in this stack, is the `initiate_swap`
method which calls the `deduct` and `deposit` methods
on two wallets owned by the same individual allowing the
user move funds from one wallet to the other. This function
can be found in the `core` module in the `utils.py` file.

The highest level of this stack can be found in the `swap`
module, with the the most important file being the `models.py`
file, which contains a `Swap` model. This model contains a
`swap_currency` model which calls the previously mentioned
`initiate_swap` method whenever a new `Swap` model is saved.


### Instructions for fiat withdrawal ###

Fiat withdrawals starts at the `deduct` method mentioned
in the swap instruction, withdrawals simply require an
amount to be removed from the users wallet and the
fiat agents notified of the transaction to send the
mentioned amount to the users bank account.
The `deduct` method handles the removal of funds and the
fiat agents are notified by the `notify_withdraw_handler`
which is found in the `models.py` of the `wallets` module.
These functions are finally called in the `WithdrawAPIView`
view of the `views.py` file of the `transactions` module.
