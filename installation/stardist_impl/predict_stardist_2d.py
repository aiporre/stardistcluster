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
from csbdeep.data import PercentileNormalizer
import numpy as np
from stardist.models import StarDist2D


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
def run_prediction(image_files, model_path, output_dir, multichannel, memory_reduction):


    # load the model
    model_root, model_name = os.path.split(model_path.rstrip('/'))
    model = StarDist2D(None, name=model_name, basedir=model_root)

    os.makedirs(output_dir, exist_ok=True)

    # normalization parameters: lower and upper percentile used for image normalization
    # maybe these should be exposed
    lower_percentile = 1
    upper_percentile = 99.8
    ax_norm = (0, 1)  # independent normalization for multichannel images

    for im_file in tqdm(image_files, desc="run stardist prediction"):
        if multichannel:
            im = imageio.volread(im_file).transpose((1, 2, 0))
        else:
            im = imageio.imread(im_file)

        if memory_reduction < 0:
            print('Prediction on Memory. No memory reduction')
            im = normalize(im, lower_percentile, upper_percentile, axis=ax_norm)
            pred, _ = model.predict_instances(im)

        else:
            print('Memory reduction ', memory_reduction, '%')
            memory_reduction = memory_reduction/100
            if len(model.config.axes)>3:
                print(f'Warning: Model {model.config.axes} axes configutation doesn\'t match image dimensions {im.shape}. Using ZYX from ax_norm={ax_norm}')
                axes ='ZYX'
            else:
                axes = model.config.axes
            normalizer = PercentileNormalizer(lower_percentile, upper_percentile)
            print('Computing with memory reduction usage ', memory_reduction/100, "% of original size")
            memory_reduction = memory_reduction/100
            block_size = [int(memory_reduction*s) for s in im.shape]
            min_overlap= [int(0.1*b) for b in block_size]
            context= [int(0.3*b) for b in block_size]

            for size, bz, mo, c in zip(im.shape, block_size, min_overlap, context):
                assert 0 <= mo + 2 * c < bz <= size, '0 <= min_overlap + 2 * context < block_size <= size'
                assert bz > 0, 'block_size > 1'
            print(f'min_overlap = {min_overlap} context = {context}, block_size = {block_size}, size ={im.shape}')
            from tempfile import mkdtemp
            import os.path as path
            filename = path.join('D:/stardistcluster/', 'temp_labels.dat')
            print("created temporal label prediction file at: ", filename)
            labels_out = np.memmap(filename, dtype='int32', mode='w+', shape=im.shape)
            pred, _ = model.predict_instances_big(im,
                                                  axes=axes,
                                                  block_size=block_size,
                                                  min_overlap=min_overlap,
                                                  context=context,
                                                  n_tiles=model._guess_n_tiles(im),
                                                  normalizer=normalizer,
                                                  labels_out=labels_out
                                                  )
            size = im.shape
            del im
            pred = np.fromfile(filename, np.int32).reshape(size)
            os.remove(filename)
            if os.path.exists(filename):
                print('Warning: file still exists delete it manually.: ', filename)
            labels_out.flush()


        im_name = os.path.split(im_file)[1]
        save_path = os.path.join(output_dir, im_name)
        imageio.imsave(save_path, pred)


def predict_stardist(model_path, input_dir, output_dir, ext, multichannel, memory_reduction):
    print("Loading images")
    image_files = get_image_files(input_dir, ext)
    print("Found", len(image_files), "images for prediction")

    print("Start prediction ...")
    run_prediction(image_files, model_path, output_dir, multichannel, memory_reduction)
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
    parser.add_argument('--multichannel', action='store_true', help="Do we have multichannel images? Default: 0")
    parser.add_argument('-r', '--memory-reduction', type=int, default=-1,
                        help="Memory reduction (-1 means it uses the whole memory). Defaults -1")

    args = parser.parse_args()
    model_path = os.path.join(args.models_dir,args.model_name)
    predict_stardist(model_path, args.input_dir, args.output_dir, args.ext, args.multichannel, args.memory_reduction)

if __name__ == '__main__':
    main()
