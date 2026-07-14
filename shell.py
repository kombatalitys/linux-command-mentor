import wx
import requests
import threading

# =====================================================================
# 1. SECURE AUTHENTICATION DIALOG
# =====================================================================
class AuthDialog(wx.Dialog):
    def __init__(self, parent, server_url):
        super().__init__(parent, title="Login - Linux Command Mentor", size=(350, 260))
        self.server_url = server_url
        self.token = None  # Holds our security token on successful login
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # Email Input Block
        email_label = wx.StaticText(panel, label="Email:")
        self.email_input = wx.TextCtrl(panel)
        vbox.Add(email_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add(self.email_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Password Input Block
        pass_label = wx.StaticText(panel, label="Password:")
        self.pass_input = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        vbox.Add(pass_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox.Add(self.pass_input, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        # Action Buttons (Login / Register)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        login_btn = wx.Button(panel, label="Log In")
        login_btn.Bind(wx.EVT_BUTTON, self.on_login)
        btn_sizer.Add(login_btn, 1, wx.ALL, 5)
        
        register_btn = wx.Button(panel, label="Register")
        register_btn.Bind(wx.EVT_BUTTON, self.on_register)
        btn_sizer.Add(register_btn, 1, wx.ALL, 5)
        
        vbox.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, 15)
        
        panel.SetSizer(vbox)
        self.Centre()

    def on_login(self, event):
        email = self.email_input.GetValue().strip()
        password = self.pass_input.GetValue().strip()
        
        if not email or not password:
            wx.MessageBox("Please fill in both fields.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        try:
            response = requests.post(
                f"{self.server_url}/login", 
                json={"email": email, "password": password}, 
                timeout=10
            )
            if response.status_code == 200:
                self.token = response.json().get("token")
                self.EndModal(wx.ID_OK)  # Success, close dialog
            else:
                error_msg = response.json().get("error", "Login failed.")
                wx.MessageBox(error_msg, "Login Failed", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"Could not connect to server: {str(e)}", "Connection Error", wx.OK | wx.ICON_ERROR)

    def on_register(self, event):
        email = self.email_input.GetValue().strip()
        password = self.pass_input.GetValue().strip()
        
        if not email or not password:
            wx.MessageBox("Please fill in both fields.", "Error", wx.OK | wx.ICON_ERROR)
            return
            
        try:
            response = requests.post(
                f"{self.server_url}/register", 
                json={"email": email, "password": password}, 
                timeout=10
            )
            if response.status_code == 201:
                wx.MessageBox(
                    "Registration successful!\nPlease check your email inbox for a verification link before logging in.", 
                    "Success", 
                    wx.OK | wx.ICON_INFORMATION
                )
            else:
                error_msg = response.json().get("error", "Registration failed.")
                wx.MessageBox(error_msg, "Registration Failed", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            wx.MessageBox(f"Could not connect to server: {str(e)}", "Connection Error", wx.OK | wx.ICON_ERROR)


# =====================================================================
# 2. MAIN APPLICATION FRAME
# =====================================================================
class LinuxMentorFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(600, 500))
        
        self.SERVER_BASE_URL = "https://linux-command-mentor.onrender.com"
        self.auth_token = None

        # --- A. Intercept Startup with Authentication Screen ---
        auth_dlg = AuthDialog(self, self.SERVER_BASE_URL)
        if auth_dlg.ShowModal() == wx.ID_OK:
            self.auth_token = auth_dlg.token  # Secure authentication token saved
            auth_dlg.Destroy()
        else:
            auth_dlg.Destroy()
            self.Close()  # Exit application if login window is cancelled
            return

        # --- B. Main Application Layout ---
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 1. Input Section Label
        input_label = wx.StaticText(panel, label="Enter Linux Command or Question:")
        main_sizer.Add(input_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # 2. Input Text Box
        self.entry = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.entry.Bind(wx.EVT_TEXT_ENTER, self.on_check_command)
        main_sizer.Add(self.entry, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # 3. Action Button
        self.submit_btn = wx.Button(panel, label="Explain Command")
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_check_command)
        main_sizer.Add(self.submit_btn, 0, wx.ALL | wx.CENTER, 10)

        # 4. Label for Output Section
        output_label = wx.StaticText(panel, label="Explanation:")
        main_sizer.Add(output_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # 5. Output Box: Read-Only, Multi-line focusable text control so NVDA can read it smoothly
        self.output_display = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )
        main_sizer.Add(self.output_display, 1, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(main_sizer)
        self.Centre()
        self.Show()

    # =====================================================================
    # 3. GUI EVENTS AND BACKGROUND NETWORKING
    # =====================================================================
    def on_check_command(self, event):
        user_input = self.entry.GetValue().strip()

        if not user_input:
            self.output_display.SetValue("Please type a command first!")
            return

        self.output_display.SetValue("Contacting AI proxy server...")

        # Network call placed in a worker thread so the GUI doesn't freeze NVDA
        threading.Thread(
            target=self.fetch_explanation, 
            args=(user_input,), 
            daemon=True
        ).start()

    def fetch_explanation(self, command):
        try:
            SERVER_URL = f"{self.SERVER_BASE_URL}/chat"
            
            # Pack the Supabase security token inside the request header
            headers = {
                "Authorization": f"Bearer {self.auth_token}"
            }
            
            response = requests.post(
                SERVER_URL, 
                json={"prompt": command}, 
                headers=headers, 
                timeout=15
            )

            if response.status_code == 200:
                ai_response = response.json().get("response")
                # Safely update GUI output field from background thread using CallAfter
                wx.CallAfter(self.output_display.SetValue, ai_response)
            else:
                error_msg = response.json().get("error", "An unknown server error occurred.")
                wx.CallAfter(self.output_display.SetValue, f"Server Error: {error_msg}")

        except Exception as e:
            wx.CallAfter(self.output_display.SetValue, f"Connection Failed: {str(e)}")


# =====================================================================
# 4. PROGRAM START ENTRYPOINT
# =====================================================================
if __name__ == "__main__":
    app = wx.App()
    LinuxMentorFrame(None, title="Linux Command Mentor")
    app.MainLoop()