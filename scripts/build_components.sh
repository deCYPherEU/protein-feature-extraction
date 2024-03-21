#!/bin/bash

function usage {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -d, --directory <directory>                 Directory containing components to build as subdirectories. The path should be relative to the root directory (default:components)"
    echo "  -t, --tag <tag>                             Tag of the component to build (default: latest)"
    echo "  -r, --registry <registry>                   Registry to push the image to (default: ghcr.io/decyphereu)"
    echo "  -f, --fondant-version <fondant-version>     Version of fondant to use (default: main)"
    echo "  -h, --help                                  Show this help message and exit"
}


# Parse the command line arguments
while [ "$1" != "" ]; do
    case $1 in
        -d | --directory )      shift
                                DIRECTORY=$1
                                ;;
        -t | --tag )            shift
                                TAG=$1
                                ;;
        -r | --registry )       shift
                                REGISTRY=$1
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        -f | --fondant-version ) shift
                                FONDANT_VERSION=$1
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

# Set default values
DIRECTORY=${DIRECTORY:-components}
TAG=${TAG:-latest}
REGISTRY=${REGISTRY:-ghcr.io/decyphereu}

# Get the list of components to build
if [ -d $DIRECTORY ]; then
    COMPONENTS=$(ls $DIRECTORY)
else
    echo "Directory $DIRECTORY does not exist"
    exit 1
fi

# Build the components
for component in $COMPONENTS; do
    echo "Building component: $component"
    FULL_IMAGE_NAME=${REGISTRY}/${component}:${TAG}
    echo "Full image name: $FULL_IMAGE_NAME"
    FONDANT_VERSION=${FONDANT_VERSION:-main}
    echo "Using fondant version: $FONDANT_VERSION"
    docker build --push -t $FULL_IMAGE_NAME --build-arg="FONDANT_VERSION=$FONDANT_VERSION" --no-cache $DIRECTORY/$component
done
