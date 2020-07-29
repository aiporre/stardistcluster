''''MIT License

Copyright (c) 2020 Constantin Pape

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import argparse
import os
from glob import glob

import imageio
from tqdm import tqdm

from csbdeep.utils import normalize
from stardist.models import StarDist3D


def get_image_files(input_dir, ext):
    # get the image and label mask paths and validate them
    image_pattern = os.path.join(input_dir, f'*{ext}')
    print("Looking for images with the pattern", image_pattern)
    images = glob(image_pattern)
    assert len(images) > 0, "Did not find any images"
    images.sort()

    return images

# could be done more efficiently, see
# https://github.com/hci-unihd/batchlib/blob/master/batchlib/segmentation/stardist_prediction.py
def run_prediction(image_files, model_path, output_dir):

    # load the model
    print('loading model..')
    model_root, model_name = os.path.split(model_path.rstrip('/'))
    model = StarDist3D(None, name=model_name, basedir=model_root)
    os.makedirs(output_dir, exist_ok=True)
    print('created output dir:', output_dir)

    # normalization parameters: lower and upper percentile used for image normalization
    # maybe these should be exposed
    lower_percentile = 1
    upper_percentile = 99.8
    ax_norm = (0, 1, 2)

    for im_file in tqdm(image_files, desc="run stardist prediction"):
        im = imageio.volread(im_file)
        im = normalize(im, lower_percentile, upper_percentile, axis=ax_norm)
        pred, _ = model.predict_instances(im)

        im_name = os.path.split(im_file)[1]
        save_path = os.path.join(output_dir, im_name)
        imageio.imsave(save_path, pred)
        print('output done:', save_path, pred)


def predict_stardist(model_path, input_dir, output_dir, ext):
    print("Loading images")
    image_files = get_image_files(input_dir, ext)
    print("Found", len(image_files), "images for prediction")

    print("Start prediction ...")
    run_prediction(image_files, model_path, output_dir)
    print("Finished prediction")


def main():
    parser = argparse.ArgumentParser(description="Predict new images with a stardist model")
    parser.add_argument('-i', '--input-dir', type=str, help="input directory contains input images.")
    parser.add_argument('-m', '--model-name', type=str,
                        help='models name in the models directory')
    parser.add_argument('-n', '--models-dir', type=str,
                        help='directory where models are loaded')
    parser.add_argument('-o', '--output-dir', type=str, default='Null',
                        help='output directory where the predicted images are saved')
    parser.add_argument('--ext', type=str, default='.tif', help="Image file extension, default: .tif")

    args = parser.parse_args()
    model_path = os.path.join(args.models_dir, args.model_name)


    predict_stardist(model_path, args.input_dir, args.output_dir, args.ext)


if __name__ == '__main__':
    main()
