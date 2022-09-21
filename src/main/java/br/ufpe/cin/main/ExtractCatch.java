package br.ufpe.cin.main;

import java.io.FileInputStream;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;

import com.github.javaparser.JavaParser;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.stmt.CatchClause;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class ExtractCatch extends SimpleFileVisitor<Path> {

    // private static final String FILE_PATH =
    // "java-parser/src/main/resources/OTFSubSetFile.java-2-Extract
    // Method-37-writeTopDICT";

    public static void main(String[] args) throws Exception {

        // if (args.length < 1) {
        //     throw new IllegalArgumentException("Not enough arguments!");
        // }

        // String FILE_PATH = args[0];
        String FILE_PATH = "/home/r4ph21/desenv/java-parser/src/main/resources/ArithmeticExceptionDemo.java";

        CompilationUnit cu_before = StaticJavaParser.parse(new FileInputStream(FILE_PATH));

        cu_before.accept(new VoidVisitorAdapter<Void>() {

            /**
             * For every if-statement, see if it has a comparison using "!=". Change it to
             * "==" and switch the "then" and "else" statements around.
             * 
             * @return
             */
            @Override
            public void visit(CatchClause cc, Void arg) {

                String filePath = FILE_PATH; // FILE_PATH.substring(FILE_PATH.lastIndexOf("-") + 1).replace(".java",
                                             // "");

                // System.out.println("Method Before Extracted from File: " + methodName);
                System.out.println("* getParameter: " + cc.getParameter());
                System.out.println(" * Position * " + cc.getBegin());
                System.out.println(" * Body * " + cc.getBody());
                System.out.println(" * Declaration * " + cc.getBody());

                // String extractedMethod =
                // md.getDeclarationAsString().concat(md.getBody().stream().findFirst().get().toString());
                // System.out.println(" * Extracted Method * " + extractedMethod);
                // outputPath = concat(new File(FILE_PATH).getParent())
                // String outputPath = FILE_PATH.concat("-Extracted");
                // String extractedMethodFormated = extractedMethod.replaceAll("\n", "
                // ").trim().replaceAll("\\s{2,}", " ");
                // System.out.println(" * Extracted Method * " + extractedMethodFormated);

            }
        }, null);

    }

}