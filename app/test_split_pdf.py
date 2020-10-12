import pytest
import os
import shutil
import split_pdf
import PIL


@pytest.fixture()
def test_files_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files/')


@pytest.fixture()
def test_temp_dir_abs_path_pdf_as_imgs(test_files_dir):
    return os.path.join(test_files_dir, 'test_temp_dir_pdf_as_imgs/')


@pytest.fixture()
def test_temp_dir_abs_path_half_imgs(test_files_dir):
    return os.path.join(test_files_dir, 'half_imgs/')


@pytest.fixture()
def test_temp_dir_abs_path_img_crop(test_files_dir):
    return os.path.join(test_files_dir, 'cropped_imgs/')


@pytest.fixture()
def test_temp_dir_abs_path_img_resize(test_files_dir):
    return os.path.join(test_files_dir, 'resized_imgs/')


@pytest.fixture
def two_slide_pdf_filename(test_files_dir):
    return "2_slides_3_pgs.pdf"

@pytest.fixture
def four_slide_pdf_filename(test_files_dir):
    return "4_slides_3_pgs.pdf"


@pytest.fixture
def two_slide_pdf_abs_path(test_files_dir, two_slide_pdf_filename):
    return os.path.join(test_files_dir, two_slide_pdf_filename)

@pytest.fixture
def four_slide_pdf_abs_path(test_files_dir, four_slide_pdf_filename):
    return os.path.join(test_files_dir, four_slide_pdf_filename)

@pytest.fixture
def two_slide_mode():
    return 3


@pytest.fixture
def four_slide_mode():
    return 0

@pytest.fixture
def uuid_file_list():
    return ['98d0b582-5b10-4377-8edc-39079905d9f0-0.ppm', '98d0b582-5b10-4377-8edc-39079905d9f0-2.ppm', '98d0b582-5b10-4377-8edc-39079905d9f0-1.ppm', '98d0b582-5b10-4377-8edc-39079905d9f0-11.ppm']

@pytest.fixture
def indexed_ppm_file_list():
    return ['6.ppm', '11.ppm', '5.ppm', '1.ppm', '9.ppm']


def delete_all_imgs(temp_dir):
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)


def assert_two_slide_files_exist(test_files_dir, two_slide_pdf_filename):
    assert os.path.isfile(os.path.join(test_files_dir, two_slide_pdf_filename))

def assert_two_slide_files_exist(test_files_dir, four_slide_pdf_filename):
    assert os.path.isfile(os.path.join(test_files_dir, four_slide_pdf_filename))

def test_convert_from_path(two_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs):
    split_pdf.extract_images_from_pdf(
        two_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs)
    delete_all_imgs(test_temp_dir_abs_path_pdf_as_imgs)


def test_list_files_in_dir(test_temp_dir_abs_path_pdf_as_imgs, two_slide_pdf_abs_path):
    split_pdf.extract_images_from_pdf(
        two_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs)
    assert len(split_pdf.list_files_in_dir(
        test_temp_dir_abs_path_pdf_as_imgs)) > 0
    delete_all_imgs(test_temp_dir_abs_path_pdf_as_imgs)


def test_get_reference_image(two_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs):
    split_pdf.extract_images_from_pdf(
        two_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs)
    first_img = split_pdf.get_reference_image(
        test_temp_dir_abs_path_pdf_as_imgs)
    assert type(first_img) == PIL.PpmImagePlugin.PpmImageFile
    delete_all_imgs(test_temp_dir_abs_path_pdf_as_imgs)


def test_process_2_slides_pdf(two_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs, two_slide_pdf_filename, test_files_dir, test_temp_dir_abs_path_half_imgs, test_temp_dir_abs_path_img_crop, test_temp_dir_abs_path_img_resize):
    split_pdf.extract_images_from_pdf(
        two_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs)
    first_img = split_pdf.get_reference_image(
        test_temp_dir_abs_path_pdf_as_imgs)

    output_document_filename = split_pdf.process_2_slide_pdf(
        test_temp_dir_abs_path_pdf_as_imgs, two_slide_pdf_filename, test_files_dir, test_files_dir, first_img, test_temp_dir_abs_path_half_imgs, test_temp_dir_abs_path_img_crop, test_temp_dir_abs_path_img_resize)

    #cleanup
    delete_all_imgs(test_temp_dir_abs_path_pdf_as_imgs)
    delete_all_imgs(test_temp_dir_abs_path_half_imgs)
    delete_all_imgs(test_temp_dir_abs_path_img_crop)
    delete_all_imgs(test_temp_dir_abs_path_img_resize)

def test_process_4_slides_pdf(four_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs, four_slide_pdf_filename, test_files_dir, test_temp_dir_abs_path_img_crop, test_temp_dir_abs_path_img_resize):
    split_pdf.extract_images_from_pdf(
        four_slide_pdf_abs_path, test_temp_dir_abs_path_pdf_as_imgs)
    first_img = split_pdf.get_reference_image(
        test_temp_dir_abs_path_pdf_as_imgs)

    output_document_filename = split_pdf.process_4_slide_pdf(
        test_temp_dir_abs_path_pdf_as_imgs, four_slide_pdf_filename, test_files_dir, test_files_dir, first_img, test_temp_dir_abs_path_img_crop, test_temp_dir_abs_path_img_resize)

    #cleanup
    delete_all_imgs(test_temp_dir_abs_path_pdf_as_imgs)
    delete_all_imgs(test_temp_dir_abs_path_img_crop)
    delete_all_imgs(test_temp_dir_abs_path_img_resize)

def test_sort_file_list_uuid(uuid_file_list):
    sorted_filenames = split_pdf.sort_file_list_uuid(uuid_file_list)
    assert sorted_filenames[0] == '98d0b582-5b10-4377-8edc-39079905d9f0-0.ppm'
    assert sorted_filenames[1] == '98d0b582-5b10-4377-8edc-39079905d9f0-1.ppm'
    assert sorted_filenames[2] ==  '98d0b582-5b10-4377-8edc-39079905d9f0-2.ppm'
    assert sorted_filenames[3] == '98d0b582-5b10-4377-8edc-39079905d9f0-11.ppm'
    
def test_get_filename_identifier():
    int_identifier = split_pdf.get_filename_int_identifier_from_uuid('98d0b582-5b10-4377-8edc-39079905d9f0-11.ppm')
    assert int_identifier == 11

def sort_file_list_indexed_ppm(indexed_ppm_file_list):
    sorted_filenames = split_pdf.sort_file_list_indexed_ppm(indexed_ppm_file_list)
    assert sorted_filenames[0] == '1.ppm'
    assert sorted_filenames[1] == '5.ppm'
    assert sorted_filenames[2] == '6.ppm'
    assert sorted_filenames[3] == '9.ppm'
    assert sorted_filenames[4] == '11.ppm'

def test_get_filename_int_identifier_from_indexed_ppm():
    int_identifier = split_pdf.get_filename_int_identifier_from_indexed_ppm('11.ppm')
    assert int_identifier == 11