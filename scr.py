import requests
import json
import zipfile
import re


def startDownload(project_id):
    print('downloading project: ' + str(project_id))

    # try:
    resp = requests.get(
        'https://cdn.projects.scratch.mit.edu/internalapi/project/'
        + str(project_id)
        + '/get/')
    project = resp.json()
    print('load json data success')
    costumesToDownload, soundsToDownload = [], []
    processSoundAndCostumes(project, costumesToDownload, soundsToDownload)
    if 'children' in project:
        for child in project['children']:
            processSoundAndCostumes(
                child, costumesToDownload, soundsToDownload)
    totalAssets = len(costumesToDownload) + len(soundsToDownload)
    print("Found %d assets" % totalAssets)

    print('Loading project title...')
    resp = requests.get('https://scratch.mit.edu/api/v1/project/' +
                        str(project_id) + '/?format=json')
    print('generate ZIP...')
    title_data = resp.json()
    zipfile_name = title_data['title'] + '.sb2'

    sb2 = zipfile.ZipFile(zipfile_name, 'w')
    sb2.writestr('project.json', json.dumps(project).encode())
    downloadCostume(sb2, costumesToDownload, soundsToDownload)

    sb2.close()
    # except Exception as e:
    #    print('error with %s', str(e))


def downloadCostume(sb2, costumesToDownload, soundsToDownload):
    complete, totalAssets = 0, len(costumesToDownload) + len(soundsToDownload)
    for costume in costumesToDownload:
        print('Loading asset ' + costume['costumeName'] + ' (' +
              str(complete) + '/' + str(totalAssets) + ')')
        resp = requests.get(
            'https://cdn.assets.scratch.mit.edu/internalapi/asset/' +
            costume['baseLayerMD5'] + '/get/')
        ext = re.findall('\.[a-zA-Z0-9]+', costume['baseLayerMD5'])[0]
        filename = str(costume['baseLayerID']) + ext
        sb2.writestr(filename, resp.content)
        complete += 1

    for costume in soundsToDownload:
        print('Loading asset ' + costume['soundName'] + ' (' +
              str(complete) + '/' + str(totalAssets) + ')')
        resp = requests.get(
            'https://cdn.assets.scratch.mit.edu/internalapi/asset/' +
            costume['md5'] + '/get/')
        ext = re.findall('\.[a-zA-Z0-9]+', costume['md5'])[0]
        filename = str(costume['soundID']) + ext
        sb2.writestr(filename, resp.content)
        complete += 1


def processSoundAndCostumes(project, c, s):
    if 'costumes' in project:
        for data in project['costumes']:
            data['baseLayerID'] = len(c)
            c.append(data)
    if 'sounds' in project:
        for data in project['sounds']:
            data['soundID'] = len(s)
            s.append(data)
