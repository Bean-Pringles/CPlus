import re
import sys
import os
import subprocess
import platform

def is_windows():
    return platform.system() == "Windows"

def compileC(filename, args):
    try:
        if "-c" not in args:
            # Determine output executable name based on OS
            if is_windows():
                output_name = filename[:-2] + ".exe"
            else:
                output_name = filename[:-2]
            
            try:
                subprocess.run(["gcc", filename, "-o", output_name], check=True)
            except subprocess.CalledProcessError as e:
                print(f"[Error] GCC compilation failed: {e}")
                return
            except FileNotFoundError:
                print("[Error] GCC compiler not found. Please ensure GCC is installed and in your PATH.")
                return

            try:
                if os.path.exists(os.path.abspath(filename)):
                    os.remove(os.path.abspath(filename))
            except Exception as e:
                print(f"[Warning] Could not remove temporary file '{filename}': {e}")

            if "-r" in args:
                # Determine executable path based on OS
                if is_windows():
                    fileexe = filename[:-2] + ".exe"
                else:
                    fileexe = "./" + filename[:-2]
                
                try:
                    subprocess.run([fileexe], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"[Error] Program execution failed with exit code {e.returncode}")
                except FileNotFoundError:
                    print(f"[Error] Executable not found: {fileexe}")
                except Exception as e:
                    print(f"[Error] Failed to run executable: {e}")

                if "-d" in args:
                    try:
                        if is_windows():
                            exe_path = os.path.abspath(filename[:-2] + ".exe")
                        else:
                            exe_path = os.path.abspath(filename[:-2])
                        
                        if os.path.exists(exe_path):
                            os.remove(exe_path)
                    except Exception as e:
                        print(f"[Warning] Could not remove executable '{exe_path}': {e}")
    except Exception as e:
        print(f"[Error] Unexpected error in compileC: {e}")

def writeFile(args, filepath):
    try:
        line = ""
        
        line = "".join(args)

        try:
            with open(filepath, 'a') as file:
                file.write(line)
        except FileNotFoundError:
            print(f"[Error] File not found at '{filepath}'")
        except PermissionError:
            print(f"[Error] Permission denied when writing to '{filepath}'")
        except Exception as e:
            print(f"[Error] An error occurred while writing: {e}")
    except Exception as e:
        print(f"[Error] Unexpected error in writeFile: {e}")

def countLines(filepath):
    try:
        with open(filepath, 'r') as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        print(f"[Error] File not found: '{filepath}'")
        return -1
    except PermissionError:
        print(f"[Error] Permission denied when reading '{filepath}'")
        return -1
    except Exception as e:
        print(f"[Error] Could not count lines in '{filepath}': {e}")
        return -1

def getLine(filename, n):
    try:
        with open(filename, 'r') as f:
            for i, line in enumerate(f, start=1):
                if i == n:
                    return line.rstrip("\n")
        return None
    except FileNotFoundError:
        print(f"[Error] File not found: '{filename}'")
        return None
    except PermissionError:
        print(f"[Error] Permission denied when reading '{filename}'")
        return None
    except Exception as e:
        print(f"[Error] Could not read line {n} from '{filename}': {e}")
        return None

def regexEngine(line):
    try:
        # keeps whitespace tokens, words, symbols
        pattern = r"""
            //.*                              | # single-line comments
            /\*[\s\S]*?\*/                    | # multi-line comments
            >=|<=|!=|==|->                     | # multi-char operators
            [A-Za-z_][A-Za-z0-9_]*            | # identifiers
            [(){}:;=+\-*/<>]                  | # single-char operators
            \s+                                | # whitespace
            .
        """

        return re.findall(pattern, line, re.VERBOSE)
    except Exception as e:
        print(f"[Error] Regex parsing failed on line: '{line}': {e}")
        return []

def compileLine(tokens):
    try:
        global inMultilineComment
        
        tokens = [t for t in tokens if not t.strip().startswith("//")]

        if tokens:
            if tokens[len(tokens) - 1] == "":
                del tokens[len(tokens) - 1]

            if tokens[-1].isspace():
                tokens.pop()

        if not tokens or "".join(tokens).strip() == "":
            return ["\n"]
        
        try:
            if "/" in tokens:
                slashIndex = tokens.index("/")
                if slashIndex > 0 and tokens[slashIndex - 1] == "*":
                    starIndex = slashIndex - 1
                    tokens[starIndex] = "*/"
                    del tokens[starIndex + 1]
                    inMultilineComment = 0

            if "/" in tokens:
                slashIndex = tokens.index("/")
                if slashIndex + 1 < len(tokens) and tokens[slashIndex + 1] == "*":
                    starIndex = slashIndex + 1
                    tokens[starIndex] = "/*"
                    del tokens[starIndex - 1]
                    inMultilineComment = 1
        
        except Exception as e:
            print(f"[Warning] Error processing comment tokens: {e}")

        if inMultilineComment == 0:
            # ---- let statement ----
            if "let" in tokens:
                try:
                    idx = tokens.index("let")

                    # let* <name>: <type> = <value>
                    if "*" in tokens:
                        # Expect structure: let* <name>: <type> = <value>
                        # Find variable name, colon, type
                        try:
                            name = tokens[idx + 3]
                            vartype = tokens[idx + 6]
                        except:
                            return tokens  # malformed line

                        # Replace "let" with C type
                        if vartype in ["int", "float", "double"]:
                            tokens[idx] = vartype
                         
                            del tokens[idx + 6]  # remove type
                            del tokens[idx + 4]  # remove colon
                            del tokens[idx + 5]
                            tokens.insert(idx + 7, "&")

                        # char *b = a;
                        # let* b: string = a
                        # Expect structure: let <name>: <type> = <value>    
                        elif vartype == "string":
                            tokens[idx] = "char" # Let to char
                            tokens[idx + 1] = " "
                            tokens[idx + 2] = "*"
                            tokens[idx + 3] = name

                            for _ in range(3):
                                del tokens[idx + 4]

                    else:
                        # Expect structure: let <name>: <type>; <unsigned>; <long/short> = <value>
                        # Find variable name, colon, type
                        unsignedVar = 0
                        longShortVar = 0
                        tempTokens = []
                        
                        if "unsigned" in tokens:
                            unsignedVar = 1
                        
                        if "long" in tokens:
                            if tokens[tokens.index("long") + 2] == "long":
                                longShortVar = 2
                            else:
                                longShortVar = 1
                        
                        elif "short" in tokens:
                            longShortVar = 1
                        
                        try:
                            name = tokens[idx + 2]
                            vartype = tokens[idx + 5]
                        except:
                            return tokens

                        if vartype in ["int", "float", "double"]:
                            tokens[idx] = vartype
                            del tokens[idx + 4] # int <name> <type>; <unsigned>; <long/short> = <value>

                            if unsignedVar == 1 or longShortVar == 1:
                                tempTokens.append(tokens[idx + 7])
                                del tokens[idx + 7] # int <name> <type>; = <value>
                                
                                for _ in range(4):
                                    del tokens[idx + 3]

                                tokens.insert(idx, " ")
                                tokens.insert(idx, tempTokens[0])

                                if unsignedVar + longShortVar == 2 and longShortVar != 2:
                                    # unsigned int a; long = 4;
                                    tokens.insert(idx + 2, tokens[idx + 7])
                                    tokens.insert(idx + 3, " ")

                                    del tokens[idx + 7]
                                    del tokens[idx + 7]
                                    del tokens[idx + 7]
                                
                                elif longShortVar == 2:
                                    # unsigned int a; long long = 4;
                                    tokens.insert(idx + 2, "long")
                                    tokens.insert(idx + 3, " ")
                                    tokens.insert(idx + 4, "long")
                                    tokens.insert(idx + 5, " ") # unsigned long long int a; long long = 4;
                                    
                                    for _ in range(5):
                                        del tokens[idx + 9]

                            if longShortVar == 2 and unsignedVar == 0:
                                # unsigned int a; long long = 4;
                                tokens.insert(idx, "long")
                                tokens.insert(idx + 1, " ")
                                tokens.insert(idx + 2, "long")
                                tokens.insert(idx + 3, " ") # unsigned long long int a; long long = 4;

                                for _ in range(7):
                                    del tokens[idx + 7]
                        
                        elif "string" in tokens:
                            # let x: string; unsigned = 1
                            tokens[idx] = "char"
                            tokens[idx + 3] = "[]" # char x[] string; unsigned = 1
                            
                            del tokens[idx + 4]
                            del tokens[idx + 4] # char x[]; unsigned = 1

                            if unsignedVar == 1:
                                for _ in range(3):
                                    del tokens[idx + 4]
                                tokens.insert(idx, "unsigned")
                                tokens.insert(idx + 1, " ")

                except Exception as e:
                    print(f"[Warning] Error processing 'let' statement: {e}")

            # ---- function keyword ----
            if "fn" in tokens:
                try:
                    if "->" in tokens:
                        start = tokens.index("fn")
                        tokens[tokens.index("fn")] = "int"
                        
                        for _ in range(4):
                            del tokens[start + 6]

                    else:
                        tokens[tokens.index("fn")] = "void"
                except Exception as e:
                    print(f"[Warning] Error processing 'fn' statement: {e}")

            # ---- print keyword ----
            if "print" in tokens:
                try:
                    tokens[tokens.index("print")] = "printf"
                except Exception as e:
                    print(f"[Warning] Error processing 'print' statement: {e}")

            # ---- import ----
            if "import" in tokens:
                try:
                    idx = tokens.index("import")
                    if idx + 2 < len(tokens):
                        tokens[idx] = "#include"
                        header = tokens[idx + 2]
                        tokens[idx + 2] = "<" + header + ".h"
                        try: 
                            tokens[idx + 3] = (">")
                        except IndexError as e:
                            tokens.append(">")
                    else:
                        print(f"[Warning] Malformed 'import' statement - not enough tokens")
                except Exception as e:
                    print(f"[Warning] Error processing 'import' statement: {e}")
            
            # append semicolon if missing
            if tokens[len(tokens) - 1] not in [";", "{", "}", ">", "/*", "*/"]:
                tokens.append(";")

        # newline always
        tokens.append("\n")
        return tokens
    except Exception as e:
        print(f"[Error] Unexpected error in compileLine: {e}")
        return ["\n"]

def main():
    try:
        if len(sys.argv) < 2:
            print("[Error] Usage: cpc <filename.cpl> [options]")
            sys.exit(1)
        
        args = sys.argv
        
        global inMultilineComment
        inMultilineComment = 0

        filename = args[1]

        if os.path.splitext(filename)[1] != ".cpl":
            print("[Error] A .cpl file is required")
            sys.exit(1)

        if not os.path.exists(filename):
            print(f"[Error] File not found: '{filename}'")
            sys.exit(1)

        cfilepath = filename[:-5] + "c"

        # remove old output
        try:
            if os.path.exists(cfilepath):
                os.remove(cfilepath)
        except Exception as e:
            print(f"[Warning] Could not remove old output file '{cfilepath}': {e}")

        numLines = countLines(filename)
        
        if numLines == -1:
            print("[Error] Failed to read input file")
            sys.exit(1)

        for n in range(1, numLines + 1):
            line = getLine(filename, n)
            if line is None:
                continue
            tokens = regexEngine(line)
            compiled = compileLine(tokens)
            writeFile(compiled, cfilepath)

        compileC(cfilepath, args)
        
    except KeyboardInterrupt:
        print("\n[Error] Compilation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"[Error] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

