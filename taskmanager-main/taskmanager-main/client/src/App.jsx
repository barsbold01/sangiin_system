import { Transition } from "@headlessui/react";
import clsx from "clsx";
import { Fragment, useRef } from "react";
import { IoClose } from "react-icons/io5";
import { useDispatch, useSelector } from "react-redux";
import { Navigate, Outlet, Route, Routes, useLocation } from "react-router-dom";
import { Toaster } from "sonner";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Login from "./pages/Login";
import TaskDetails from "./pages/TaskDetails";
import Tasks from "./pages/Tasks";
import Trash from "./pages/Trash";
import Users from "./pages/Users";
import Dashboard from "./pages/dashboard";
import { setOpenSidebar } from "./redux/slices/authSlice";

function Layout() {
  const { user } = useSelector((state) => state.auth);
  const location = useLocation();

  return user ? (
    <div className='w-full h-screen flex flex-col md:flex-row bg-[#EDE6F7] text-[#4B0082]'>
      {/* Desktop Sidebar */}
      <div className='hidden md:block w-1/5 h-screen bg-[#D6C6EE] sticky top-0 border-r-2 border-[#C4A3F5] shadow-lg'>
        <Sidebar />
      </div>

      <MobileSidebar />

      <div className='flex-1 overflow-y-auto'>
        <Navbar />

        <div className='p-4 2xl:px-10 min-h-[calc(100vh-80px)]'>
          <Outlet />
        </div>
      </div>
    </div>
  ) : (
    <Navigate to='/log-in' state={{ from: location }} replace />
  );
}

const MobileSidebar = () => {
  const { isSidebarOpen } = useSelector((state) => state.auth);
  const mobileMenuRef = useRef(null);
  const dispatch = useDispatch();

  const closeSidebar = () => {
    dispatch(setOpenSidebar(false));
  };

  return (
    <>
      <Transition
        show={isSidebarOpen}
        as={Fragment}
        enter='transition-all duration-300'
        enterFrom='opacity-0'
        enterTo='opacity-100'
        leave='transition-all duration-300'
        leaveFrom='opacity-100'
        leaveTo='opacity-0'
      >
        {(ref) => (
          <div
            ref={(node) => (mobileMenuRef.current = node)}
            className={clsx(
              "md:hidden fixed inset-0 z-50 transition-all duration-300",
              isSidebarOpen 
                ? "bg-black/20 backdrop-blur-sm" 
                : "bg-transparent pointer-events-none"
            )}
            onClick={() => closeSidebar()}
          >
            <div 
              className={clsx(
                "bg-[#D6C6EE] w-3/4 h-full transform transition-transform duration-300 ease-in-out shadow-2xl",
                isSidebarOpen ? "translate-x-0" : "-translate-x-full"
              )}
              onClick={(e) => e.stopPropagation()}
            >
              {/* Mobile sidebar header */}
              <div className='w-full flex justify-between items-center px-5 py-4 bg-[#C4A3F5] text-[#4B0082]'>
                <h2 className='text-xl font-bold'>Даалгаврын менежер</h2>
                <button
                  onClick={() => closeSidebar()}
                  className='flex items-center justify-center w-10 h-10 rounded-full hover:bg-[#F7C6D0] transition-colors duration-200'
                >
                  <IoClose size={24} className='text-[#4B0082]' />
                </button>
              </div>

              <div className='overflow-y-auto h-[calc(100%-64px)]'>
                <Sidebar />
              </div>
            </div>
          </div>
        )}
      </Transition>
    </>
  );
};

function App() {
  return (
    <main className='w-full min-h-screen bg-[#EDE6F7] text-[#4B0082]'>
      <Routes>
        <Route element={<Layout />}>
          <Route index path='/' element={<Navigate to='/dashboard' />} />
          <Route path='/dashboard' element={<Dashboard />} />
          <Route path='/tasks' element={<Tasks />} />
          <Route path='/completed/:status' element={<Tasks />} />
          <Route path='/in-progress/:status' element={<Tasks />} />
          <Route path='/todo/:status' element={<Tasks />} />
          <Route path='/team' element={<Users />} />
          <Route path='/trashed' element={<Trash />} />
          <Route path='/task/:id' element={<TaskDetails />} />
        </Route>

        <Route path='/log-in' element={<Login />} />
      </Routes>

      <Toaster 
        richColors
        toastOptions={{
          style: {
            background: '#C4A3F5',
            color: '#4B0082',
            border: 'none',
            fontSize: '14px',
          },
          className: 'font-sans',
          duration: 3000,
        }}
        position="bottom-right"
        expand={true}
        closeButton
      />
      
      <button 
        className="fixed bottom-6 right-6 w-12 h-12 rounded-full bg-[#C4A3F5] text-[#4B0082] flex items-center justify-center shadow-lg hover:bg-[#F7C6D0] transition-colors duration-200 z-40 text-xl"
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        aria-label="Scroll to top"
      >
        ↑
      </button>
    </main>
  );
}

export default App;
