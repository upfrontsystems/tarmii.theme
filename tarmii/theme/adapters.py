from plone.app.users.browser.personalpreferences import UserDataPanelAdapter

class TARMIIUserDataPanelAdapter(UserDataPanelAdapter):

    def get_fullname(self):
        return self.context.getProperty('fullname', '')
    def set_fullname(self, value):
        return self.context.setMemberProperties({'fullname': value})
    fullname = property(get_fullname, set_fullname)

    def get_username(self):
        return self.context.getProperty('username', '')
    def set_username(self, value):
        return self.context.setMemberProperties({'username': value})
    username = property(get_username, set_username)

    def get_email(self):
        return self.context.getProperty('email', '')
    def set_email(self, value):
        return self.context.setMemberProperties({'email': value})
    email = property(get_email, set_email)

    def get_school(self):
        return self.context.getProperty('school', '')
    def set_school(self, value):
        return self.context.setMemberProperties({'school': value})
    school = property(get_school, set_school)

    def get_province(self):
        return self.context.getProperty('province', '')
    def set_province(self, value):
        return self.context.setMemberProperties({'province': value})
    province = property(get_province, set_province)

    def get_EMIS(self):
        return self.context.getProperty('EMIS', '')
    def set_EMIS(self, value):
        return self.context.setMemberProperties({'EMIS': value})
    EMIS = property(get_EMIS, set_EMIS)

    def get_school_contact_number(self):
        return self.context.getProperty('school_contact_number', '')
    def set_school_contact_number(self, value):
        return self.context.setMemberProperties({'school_contact_number': value})
    school_contact_number = property(get_school_contact_number, set_school_contact_number)

    def get_school_email(self):
        return self.context.getProperty('school_email', '')
    def set_school_email(self, value):
        return self.context.setMemberProperties({'school_email': value})
    school_email = property(get_school_email, set_school_email)

    def get_qualification(self):
        return self.context.getProperty('qualification', '')
    def set_qualification(self, value):
        return self.context.setMemberProperties({'qualification': value})
    qualification = property(get_qualification, set_qualification)

    def get_years_teaching(self):
        return self.context.getProperty('years_teaching', '')
    def set_years_teaching(self, value):
        return self.context.setMemberProperties({'years_teaching': value})
    years_teaching = property(get_years_teaching, set_years_teaching)

