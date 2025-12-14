import React from "react";
import { useForm } from "react-hook-form";
import { useSelector } from "react-redux";
import ModalWrapper from "./ModalWrapper";
import { Dialog } from "@headlessui/react";
import Textbox from "./Textbox";
import Loading from "./Loader";
import Button from "./Button";

const AddUser = ({ open, setOpen, userData }) => {
  let defaultValues = userData ?? {};
  const { user } = useSelector((state) => state.auth);

  const isLoading = false,
    isUpdating = false;

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ defaultValues });

  const handleOnSubmit = () => {};

  return (
    <>
      <ModalWrapper open={open} setOpen={setOpen}>
        <form onSubmit={handleSubmit(handleOnSubmit)} className=''>
          <Dialog.Title
            as='h2'
            className='text-base font-bold leading-6 text-gray-900 mb-4'
          >
            {userData ? "ХЭРЭГЛЭГЧИЙН МЭДЭЭЛЭЛ ШИНЭЧЛЭХ" : "ШИНЭ ХЭРЭГЛЭГЧ НЭМЭХ"}
          </Dialog.Title>
          <div className='mt-2 flex flex-col gap-6'>
            <Textbox
              placeholder='Бүтэн нэр'
              type='text'
              name='name'
              label='Бүтэн нэр'
              className='w-full rounded'
              register={register("name", {
                required: "Бүтэн нэр шаардлагатай!",
              })}
              error={errors.name ? errors.name.message : ""}
            />
            <Textbox
              placeholder='Албан тушаал'
              type='text'
              name='title'
              label='Албан тушаал'
              className='w-full rounded'
              register={register("title", {
                required: "Албан тушаал шаардлагатай!",
              })}
              error={errors.title ? errors.title.message : ""}
            />
            <Textbox
              placeholder='имэйл@жишээ.com'
              type='email'
              name='email'
              label='Имэйл хаяг'
              className='w-full rounded'
              register={register("email", {
                required: "Имэйл хаяг шаардлагатай!",
              })}
              error={errors.email ? errors.email.message : ""}
            />

            <Textbox
              placeholder='Үүрэг'
              type='text'
              name='role'
              label='Үүрэг'
              className='w-full rounded'
              register={register("role", {
                required: "Хэрэглэгчийн үүрэг шаардлагатай!",
              })}
              error={errors.role ? errors.role.message : ""}
            />
          </div>

          {isLoading || isUpdating ? (
            <div className='py-5'>
              <Loading />
            </div>
          ) : (
            <div className='py-3 mt-4 sm:flex sm:flex-row-reverse'>
              <Button
                type='submit'
                className='bg-blue-600 px-8 text-sm font-semibold text-white hover:bg-blue-700  sm:w-auto'
                label='Илгээх'
              />

              <Button
                type='button'
                className='bg-white px-5 text-sm font-semibold text-gray-900 sm:w-auto'
                onClick={() => setOpen(false)}
                label='Цуцлах'
              />
            </div>
          )}
        </form>
      </ModalWrapper>
    </>
  );
};

export default AddUser;