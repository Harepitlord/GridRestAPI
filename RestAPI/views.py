from django.views import View
from django.http import HttpResponse, HttpRequest,JsonResponse
import subprocess


def csvToJson(data: str):
    csvData = data.replace("\"")
    csvData = csvData.split("\n")
    header = csvData[0].split(",")
    csvData = csvData[1:]
    csvData = [r.split(",") for r in csvData]
    jsonData = []
    for i in range(len(csvData)):
        temp = {}
        for r in range(len(header)):
            temp[header[r]] = csvData[i][r]

        jsonData.append(temp)

    return {'Data': jsonData}


class GridCommands:
    grid = "grid"
    organization = "organization"


class GridRequiredFields:
    org_Id = "Org_Id"
    org_Name = "Org_Name"


class GridOptionalFields:
    alternate_Id = "alternate-ids"
    location = "location"


def runCmd(cmd: list):
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    formattedOutput = None
    stdoutOutput = output.stdout.decode('UTF-8')
    stderrOutput = output.stderr.decode('UTF-8')

    serr = len(stderrOutput) == 0
    sout = len(stdoutOutput) == 0

    if not sout and serr:
        return stdoutOutput

    if sout and not serr:
        return stderrOutput

    if sout and serr:
        return stdoutOutput + stderrOutput

    return "Internal Command Server"


# Create your views here.
class Sample(View):
    def get(self, request):
        return HttpResponse("HELLO")


class OrganizationCreate(View):
    def post(self, request: HttpRequest):
        org_Id = request.POST.get(key="Org_Id")
        org_Name = request.POST.get(key="Org_Name")
        cmd = [GridCommands.grid, GridCommands.organization]
        cmd.extend(['create', org_Id, org_Name])
        if request.POST.__contains__('alternate_Id'):
            cmd.append(request.POST.get(key='alternate_Id'))

        output = runCmd(cmd)
        return JsonResponse({"Data":output})


class OrganizationList(View):
    def get(self, request: HttpRequest):
        cmd = [GridCommands.grid, GridCommands.organization, 'list']

        output = runCmd(cmd)
        return JsonResponse({"Data":output})


class OrganizationUpdate(View):
    def post(self, request: HttpRequest):
        org_Id = request.POST.get(key=GridRequiredFields.org_Id)
        org_Name = request.POST.get(key=GridRequiredFields.org_Name)

        cmd = [GridCommands.grid, GridCommands.organization]
        cmd.extend(['update', org_Id, org_Name])

        if request.POST.__contains__(GridOptionalFields.alternate_Id):
            cmd.extend(["--" + GridOptionalFields.alternate_Id, request.POST.get(key=GridOptionalFields.alternate_Id)])

        if request.POST.__contains__(GridOptionalFields.location):
            cmd.extend(["--" + GridOptionalFields.location, request.POST.get(key=GridOptionalFields.location)])

        output = runCmd(cmd=cmd)
        return JsonResponse({"Data":output})


class OrganizationShow(View):
    def post(self, request: HttpRequest):
        org_Id = request.POST.get(key=GridRequiredFields.org_Id)
        csv = request.POST.get(key="csv")

        cmd = [GridCommands.grid, GridCommands.organization]
        cmd.extend(['list'])

        if csv == "True":
            cmd.extend(["-F csv"])
            return JsonResponse(csvToJson(runCmd(cmd)))


