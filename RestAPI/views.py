from django.views import View
from django.http import HttpResponse, HttpRequest, JsonResponse
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
    role = "role"


class GridProcess:
    create = "create"
    update = "update"
    delete = "delete"
    list = "list"
    show = "show"


class GridRequiredFields:
    org_Id = "Org_Id"
    org_Name = "Org_Name"
    role_Name = "role_Name"
    pubKey = "pubKey"


class GridOptionalFields:
    alternate_Id = "alternate-ids"
    location = "location"
    description = "description"
    active = "active"
    permissions = "permissions"
    key = "key"
    allowed_Org = "allowed-orgs"
    inherit_From = "inherit-from"
    metadata = "metadata"
    role = "role"


class GridFlags:
    verbose = "verbose"
    quiet = "quiet"
    help = "help"
    version = "version"


def runCmd(cmd: list):
    try:
        output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
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

        if not sout and not serr:
            return "Done"

    except subprocess.CalledProcessError:
        return "Process Failed"

    return "Internal Command Server"


def addFlags(request: HttpRequest, cmd: list):
    if request.POST.__contains__(GridFlags.verbose):
        cmd.append('-v')

    if request.POST.__contains__(GridFlags.quiet):
        cmd.append('-q')

    return cmd


def addEndFlags(request: HttpRequest, cmd: list):
    endFlags = False
    if request.POST.__contains__(GridFlags.help):
        cmd.append("-h")
        endFlags = True
    if request.POST.__contains__(GridFlags.version):
        cmd.append("-v")
        endFlags = True

    if endFlags:
        return runCmd(cmd)
    return None


# Create your views here.
class Sample(View):
    def get(self, request):
        return HttpResponse("HELLO")


class Organization:
    class CreateOrganization(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key="Org_Id")
            org_Name = request.POST.get(key="Org_Name")
            cmd = [GridCommands.grid, GridCommands.organization, GridProcess.create]
            output = addEndFlags(request, cmd)
            if output is None:
                cmd.extend([org_Id, org_Name])

                addFlags(request, cmd)

                if request.POST.__contains__('alternate_Id'):
                    cmd.append(request.POST.get(key='alternate_Id'))
                output = runCmd(cmd)

            return JsonResponse({"Data": output})

    class ListOrganization(View):
        def get(self, request: HttpRequest):
            cmd = [GridCommands.grid, GridCommands.organization, GridProcess.list]
            csv = request.POST.get(key="csv")

            output = addEndFlags(request, cmd)
            if output is None:
                addFlags(request, cmd)
                if csv == "True":
                    cmd.extend(["-F csv"])
                    return JsonResponse(csvToJson(runCmd(cmd)))
                output = runCmd(cmd)
            return JsonResponse({"Data": output})

    class UpdateOrganization(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)
            org_Name = request.POST.get(key=GridRequiredFields.org_Name)

            cmd = [GridCommands.grid, GridCommands.organization, GridProcess.update]
            output = addEndFlags(request, cmd)
            if output is None:
                cmd.extend([org_Id, org_Name])

                addFlags(request, cmd)

                if request.POST.__contains__(GridOptionalFields.alternate_Id):
                    cmd.extend(
                        ["--" + GridOptionalFields.alternate_Id, request.POST.get(key=GridOptionalFields.alternate_Id)])

                if request.POST.__contains__(GridOptionalFields.location):
                    cmd.extend(["--" + GridOptionalFields.location, request.POST.get(key=GridOptionalFields.location)])

                output = runCmd(cmd=cmd)
            return JsonResponse({"Data": output})

    class ShowOrganization(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)

            cmd = [GridCommands.grid, GridCommands.organization, GridProcess.show]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.append(request.POST.get(key=GridRequiredFields.org_Id))

                addFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})


class Role:

    def addOptionalFlags(self, request: HttpRequest, cmd: list):
        if request.POST.__contains__(GridOptionalFields.description):
            cmd.extend(
                ['--' + GridOptionalFields.description, request.POST.get(key=GridOptionalFields.description)])

        if request.POST.__contains__(GridOptionalFields.permissions):
            cmd.extend(['--' + GridOptionalFields.permissions,
                        f"\"{request.POST.get(key=GridOptionalFields.permissions)}\""])

        if request.POST.__contains__(GridOptionalFields.key):
            cmd.extend(['--' + GridOptionalFields.key, request.POST.get(key=GridOptionalFields.key)])

        if request.POST.__contains__(GridOptionalFields.active):
            if request.POST.get(key=GridOptionalFields.active) == 1:
                cmd.append('--active')
            else:
                cmd.append('--inactive')

        if request.POST.__contains__(GridOptionalFields.allowed_Org):
            cmd.append('--' + GridOptionalFields.allowed_Org)
            cmd.extend(request.POST.get(GridOptionalFields.allowed_Org))

        if request.POST.__contains__(GridOptionalFields.inherit_From):
            cmd.append('--' + GridOptionalFields.inherit_From)
            cmd.extend(request.POST.get(key=GridOptionalFields.inherit_From))

    class CreateRole(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)
            role_Name = request.POST.get(key=GridRequiredFields.role_Name)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.create]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.extend([org_Id, role_Name])

                addFlags(request, cmd)

                Role.addOptionalFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})

    class UpdateRole(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)
            role_Name = request.POST.get(key=GridRequiredFields.role_Name)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.update]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.extend([org_Id, role_Name])

                addFlags(request, cmd)

                Role.addOptionalFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})

    class DeleteRole(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)
            role_Name = request.POST.get(key=GridRequiredFields.role_Name)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.delete]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.extend([org_Id, role_Name])

                addFlags(request, cmd)

                Role.addOptionalFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})

    class ListRole(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.list]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.append(org_Id)

                addFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})

    class ShowRole(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.show]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.append(org_Id)

                addFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})


class Agent:

    def addOptionalFlags(self, request: HttpRequest, cmd: list):
        if request.POST.__contains__(GridOptionalFields.metadata):
            cmd.extend(
                ['--' + GridOptionalFields.metadata, request.POST.get(key=GridOptionalFields.metadata)])

        if request.POST.__contains__(GridOptionalFields.key):
            cmd.extend(['--' + GridOptionalFields.key, request.POST.get(key=GridOptionalFields.key)])

        if request.POST.__contains__(GridOptionalFields.role):
            for r in request.POST.getlist(GridOptionalFields.role):
                cmd.extend(['--' + GridOptionalFields.role, r])

        if request.POST.__contains__(GridOptionalFields.active):
            if request.POST.get(key=GridOptionalFields.active) == 1:
                cmd.append('--active')
            else:
                cmd.append('--inactive')

    class CreateAgent(View):
        def post(self, request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)
            pubKey = request.POST.get(key=GridRequiredFields.pubKey)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.create]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.extend([org_Id, pubKey])

                Agent.addOptionalFlags(request, cmd)

                addFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})

    class UpdateAgent(View):
        def post(self,request:HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)
            pubKey = request.POST.get(key=GridRequiredFields.pubKey)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.update]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.extend([org_Id, pubKey])

                Agent.addOptionalFlags(request, cmd)

                addFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})

    class ListAgent(View):
        def post(self,request: HttpRequest):
            org_Id = request.POST.get(key=GridRequiredFields.org_Id)
            pubKey = request.POST.get(key=GridRequiredFields.pubKey)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.list]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.extend([org_Id, pubKey])

                Agent.addOptionalFlags(request, cmd)

                addFlags(request, cmd)

                if request.POST.__contains__("linePerRole"):
                    cmd.append("--line-Per-Role")
                    return JsonResponse({'data':runCmd(cmd)})
                else:
                    output = csvToJson(runCmd(cmd))

            return JsonResponse({'data': output})

    class ShowAgent(View):
        def post(self,request: HttpRequest):

            pubKey = request.POST.get(key=GridRequiredFields.pubKey)

            cmd = [GridCommands.grid, GridCommands.role, GridProcess.show]

            output = addEndFlags(request, cmd)
            if output is None:
                cmd.append(pubKey)

                addFlags(request, cmd)

                output = runCmd(cmd)

            return JsonResponse({'data': output})


class Schema:

    class CreateSchema(View):
        def post(self,request: HttpRequest):
            pass