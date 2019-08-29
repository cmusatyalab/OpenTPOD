#! /bin/bash -ex

cp -r ../cvat/cvat .

unused=('auto_annotation'
'dashboard'
'dextr_segmentation'
'git'
'reid'
)

for module in "${unused[@]}"; do
    echo "removing ${module}"
    rm -rf cvat/apps/${module}
done