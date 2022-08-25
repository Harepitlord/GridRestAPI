from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, HttpRequest
import subprocess


class commands():
    grid = "grid"
    organization = "organization"


def runCmd(cmd: list):
    output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    formattedOutput = None
    stdout = output.stdout.decode('utf-8')
    if len(output.stderr.decode('utf-8')) == 0:
        stdoutOutput = output.stdout.decode('UTF-8')
        return stdoutOutput

    if len():
        stderrOutput = output.stderr.decode('UTF-8')
        return stderrOutput

    return "Internal Command Server"


# Create your views here.
class Sample(View):
    def get(self, request):
        return HttpResponse("HELLO")


class OrganizationCreate(View):
    def post(self, request: HttpRequest):
        org_Id = request.POST.get(key="Org_Id")
        org_Name = request.POST.get(key="Org_Name")
        cmd = [commands.grid, commands.organization]
        cmd.extend(['create', org_Id, org_Name])
        if request.POST.__contains__('alternate_Id'):
            cmd.append(request.POST.get(key='alternate_Id'))

        output = runCmd(cmd)
        return HttpResponse(output)


class OrganizationList(View):
    def get(self, request: HttpRequest):
        cmd = [commands.grid,commands.organization,'list']

        output = runCmd(cmd)
        return HttpResponse(output)
