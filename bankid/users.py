class Users:

    def __init__(self):


        self.userlist = {
            'd867acb6b60e15731d9df1c4a7c386f069f3e6eb': {
                'user': 'Stian Langvann',
                'email': 'stian.langvann@gmail.com',
                'phone': '+47 942 47 659',
                'method': 'paypal',
                'expire': 1647154274
                },
            '85136c79cbf9fe36bb9d05d0639c70c265c18d37': {
                'user': 'TietoEvry AS',
                'email': 'bankingservices247@tietoevry.com',
                'phone': '+47 000 00 000',
                'method': 'free_account',
                'expire': -1 
                }
            }

        self.check()

    def check(self) -> None:
        ''' Checks for expiry '''
        pass