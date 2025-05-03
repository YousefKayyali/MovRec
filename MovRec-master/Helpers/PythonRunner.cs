using System;
using System.Diagnostics;
using System.Text;
using System.Threading.Tasks;

namespace MovRec.Helpers
{
    public static class PythonRunner
    {
        /// <summary>
        /// Runs a Python script and returns (exit-code, stdout, stderr).
        /// </summary>
        public static async Task<(int ExitCode, string StdOut, string StdErr)>
            RunAsync(string scriptPath, string arguments)
        {
            var psi = new ProcessStartInfo
            {
                FileName = "python",                  // full path if needed
                Arguments = $"{scriptPath} {arguments}",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            using var p = new Process { StartInfo = psi };

            var outBuf = new StringBuilder();
            var errBuf = new StringBuilder();

            p.OutputDataReceived += (_, e) => { if (e.Data != null) outBuf.AppendLine(e.Data); };
            p.ErrorDataReceived += (_, e) => { if (e.Data != null) errBuf.AppendLine(e.Data); };

            p.Start();
            p.BeginOutputReadLine();
            p.BeginErrorReadLine();
            await p.WaitForExitAsync();

            return (p.ExitCode, outBuf.ToString(), errBuf.ToString());
        }
    }
}