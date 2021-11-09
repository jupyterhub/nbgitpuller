# nbgitpuller - downloader plugin documentation

nbgitpuller uses [pluggy](https://pluggy.readthedocs.io/en/stable/) as a framework
to load any installed nbgitpuller-downloader plugins. There are three downloader plugins
available right now:
- [nbgitpuller-downloader-googledrive](https://github.com/jupyterhub/nbgitpuller-downloader-googledrive)
- [nbgitpuller-downloader-dropbox](https://github.com/jupyterhub/nbgitpuller-downloader-dropbox)
- [nbgitpuller-downloader-generic-web](https://github.com/jupyterhub/nbgitpuller-downloader-generic-web)


There are several pieces to be aware of for the plugin to work correctly:
1. The setup.cfg(or setup.py) file must have the entry_points definition.
For example:  

   ```toml
   [options.entry_points]  
   nbgitpuller = dropbox=nbgitpuller_downloader_dropbox.dropbox_downloader
   ```

2. The file referenced for use by nbgitpuller in the plug-in (the above example is looking for the 
file, dropbox_downloader) must implement the function handle_files(query_line_args) and be decorated with `@hookimpl`.
3. As a consequence of this, the following must be imported:
    - `from nbgitpuller.hookspecs import hookimpl`
4. The implementation of the handle_files function in your plugin needs to return
   two pieces of information:
   - the name of the folder, the archive is in after decompression
   - the path to the local git repo mimicking a remote origin repo
   
nbgitpuller provides a function in plugin_helper.py called handle_files_helper that handles the downloading
and returning of the correct information if given a URL, the extension of the
file to decompress(zip or tar) and the progress function(I will describe that
more later) but you are welcome to implement the functionality of handle_files_helper in your
plug-in. There may be use cases not covered by the currently available plugins like needing to authenticate against
the webserver or service where your archive is kept. Either way, it behooves you
to study the handle_files_helper function in nbgitpuller to get a sense of how this function
is implemented.

For the rest of the steps, I refer you to the [nbgitpuller-downloader-dropbox](https://github.com/jupyterhub/nbgitpuller-downloader-dropbox) plugin.  
   ```
   @hookimpl  
   def handle_files(query_line_args):
      query_line_args["repo"] = query_line_args["repo"].replace("dl=0", "dl=1")  # dropbox: dl set to 1  
      ext = determine_file_extension(query_line_args["repo"])`  
      query_line_args["extension"] = ext
      loop = asyncio.get_event_loop()
      tasks = handle_files_helper(query_line_args), query_line_args["progress_func"]()
      result_handle, _ = loop.run_until_complete(asyncio.gather(*tasks))
      return result_handle
   ```

The following pieces describe what happens in handle_files before, at least, in this case, we call
the handle_files_helper function:  

1) The parameter, query_line_args, is all the query line arguments you include on the nbgitpuller link. This means you 
   can put keyword arguments into your nbgitpuller links and have access to these arguments in the handle_files
   function.   
   For example, you might set up a link like this:   
   http://[your hub]/hub/user-redirect/git-pull?repo=[link to your archive]&keyword1=value1&keyword2=value2&provider=dropbox&urlpath=tree%2F%2F
   In your handle_files function, you could make this call to get your custom arguments:

   ```
   query_line_args["keyword1"]
   query_line_args["keyword2"]
   ```
2) The query_line_args parameter also includes the progress function used to monitor the download_q
   for messages; messages in the download_q are written to the UI so users can see the progress and 
   steps being taken to download their archives. You will notice the progress function is passed into 
   handle_files_helper and accessed like this:
   ```
    query_line_args["progress_func"]
    query_line_args["download_q"]
   ```
3) The first line of the handle_files function for the dropbox downloader is specific to DropBox. The URL to a file
   in DropBox contains one URL query parameter(dl=0). This parameter indicates to Dropbox whether to download the
   file or open it in their browser-based file system. In order to download the file, this parameter
   needs to be changed to dl=1. 
4) The next line determines the file extension (zip, tar.gz, etc).
   This is added to the query_lines_args map and passed off to the handle_files_helper to
   help the application know which utility to use to decompress the archive -- unzip or tar -xzf.
5) Since we don't want the user to have to wait while the download process finishes, we have made
   downloading of the archive a non-blocking process using the package asyncio. Here are the steps:
    - get the event loop
    - setup two tasks:
        - a call to the handle_files_helper with our arguments
        - the progress_loop function
    - execute the two tasks in the event loop.
6) The function returns two pieces of information to nbgitpuller:
    - the directory name of the decompressed archive
    - the local_origin_repo path.

The details of what happens in handle_files_helper can be found by studying the function. Essentially, the archive is downloaded, decompressed, and set up in a file
system to act as a remote repository(e.g. the local_origin_repo path).


