@reporting
Feature: Reporting

    Scenario: As a sysadmin, I can view and refresh the 'Tagless datasets' report
        Given "SysAdmin" as the persona
        When I log in
        And I visit "/report"
        And I click the link with text that contains "Tagless datasets"
        Then I should see an element with xpath "//select[@name='organization']"
        When I press the element with xpath "//div[contains(@class, 'panel')]//input[@type='submit']"
        Then I should see an element with xpath "//table[@id='report-table']//th[contains(string(), 'Dataset')]"
        And I should see an element with xpath "//table[@id='report-table']//th[contains(string(), 'Notes')]"
        And I should see an element with xpath "//table[@id='report-table']//th[contains(string(), 'User')]"
        And I should see an element with xpath "//table[@id='report-table']//th[contains(string(), 'Created')]"
        And I should see an element with xpath "//table[@id='report-table']//td[position()=1]/a[contains(@href, '/dataset/reporting') and contains(string(), 'Reporting dataset')]"
