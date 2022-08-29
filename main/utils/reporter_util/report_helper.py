from jinja2 import Template, Environment, FileSystemLoader
from main.model.results_model import Results
from os.path import split
import os



class ReportHelper:

    def __init__(self, uid):
        self.uuid = uid
        # Getting request and response data from database
        self.results = Results.objects(uuid=self.uuid)[0]

    def render(self, tpl_path, results, report_stats):
        path, filename = split(tpl_path)
        return Environment(
            loader=FileSystemLoader(path)
        ).get_template(filename).render(results=results,
                                        report_stats=report_stats)

    # Function to get the total no. of passed and failed testScenario
    def get_report_stats(self, results):
        stats = []
        for service in results.testExecutionInput[0].serviceName:
            stat_dict = {}
            stat_dict["service_name"] = service
            total_scenarios = 0
            total_scenarios_passed = 0
            total_scenarios_failed = 0
            for ts in results.testExecutionDetails[0].testScenarios:
                if service == ts['serviceName']:
                    total_scenarios += 1
                    if ts["tsStatus"].casefold() == "PASSED".casefold():
                        total_scenarios_passed += 1
                    else:
                        total_scenarios_failed += 1
            stat_dict["total_scenarios"] = total_scenarios
            stat_dict["total_scenarios_passed"] = total_scenarios_passed
            stat_dict["total_scenarios_failed"] = total_scenarios_failed
            stats.append(stat_dict)
        return stats

    # Function to write content to file
    def write(self, filename, data):
        read_data = []
        with open(filename, 'w') as f:
            f.write(data)

    def generateReport(self):
        # Getting path to html template file
        jinja2_template_file = os.path.realpath(os.path.join(os.path.dirname(__file__), 'report_template.html'))

        # getting path to store the html report in output folder
        output_file = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output', self.uuid+'.html'))
        output_directory = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'output')
        report_stats = self.get_report_stats(self.results)
        result = self.render(jinja2_template_file,
                             self.results,
                             report_stats)
        # writing generated html content in html report
        if not os.path.isdir(output_directory):
            os.mkdir(output_directory)

        self.write(output_file, result)