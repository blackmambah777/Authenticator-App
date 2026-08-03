from kivy.app import App
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.resources import resource_find
import shutil
import pyotp
import os
import json




def get_accounts_path():
    app = App.get_running_app()

    path = os.path.join(app.user_data_dir, "accounts.json")

    if not os.path.exists(path):
        original = resource_find("accounts.json")
        shutil.copy(original, path)

    return path


def save_account(name, secret):


    with open(get_accounts_path(), "r") as f:
        accounts = json.load(f)    

    accounts.append({
        "name": name,
        "secret": secret
    })

    # Save everything back
    with open(get_accounts_path(), "w") as f:
        json.dump(accounts, f, indent=4)
   



class AccountAddPopup(Popup):
    main_layout = ObjectProperty(None)
    def save_account(self):

        name = self.ids.name_input_field.text
        secret = self.ids.secret_input_field.text

        save_account(name, secret)

        with open(get_accounts_path(), "r") as f:
            accounts = json.load(f)
        

        print(name, secret)

        self.main_layout.load_accounts(accounts)
        self.dismiss()



class AccountRow(BoxLayout):
    name = StringProperty("")
    otp = StringProperty("000000")
    main_layout = ObjectProperty(None)


    def copy_otp(self):
        Clipboard.copy(self.otp)


    def delete_account(self):
        path = get_accounts_path()

        with open(path, "r") as f:
            accounts = json.load(f)

        accounts = [a for a in accounts if a["name"] != self.name]

        with open(path, "w") as f:
            json.dump(accounts, f, indent=4)
                
        self.parent.remove_widget(self)

class MainLayout(BoxLayout):



    def on_kv_post(self, base_widget):
        # run every second
        Clock.schedule_interval(self.update_otps, 1)

    def update_otps(self, dt):
        with open(get_accounts_path(), "r") as f:
            accounts = json.load(f)

        for widget, account in zip(reversed(self.ids.account_layout.children), accounts):
            widget.otp = pyotp.TOTP(account["secret"]).now()




    def show_popup(self):
        AccountAddPopup(main_layout=self).open()

    def load_accounts(self, accounts):
        self.ids.account_layout.clear_widgets()

        for account in accounts:
            otp = pyotp.TOTP(account["secret"]).now()
            self.ids.account_layout.add_widget(AccountRow(name=account["name"],otp=otp, main_layout=self))


class MyApp(App):
    def build(self):
        layout = MainLayout()

        with open(get_accounts_path(), "r") as f:
            accounts = json.load(f)

        layout.load_accounts(accounts)
        print(get_accounts_path())
        return layout


MyApp().run()