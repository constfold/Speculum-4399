package me.constfold.speculum

import com.jpexs.decompiler.flash.SWF
import com.jpexs.decompiler.flash.abc.ABC
import com.jpexs.decompiler.flash.abc.ScriptPack
import com.jpexs.decompiler.flash.abc.types.Multiname
import com.jpexs.decompiler.flash.abc.types.Namespace
import com.jpexs.decompiler.flash.gfx.GfxConvertor
import com.jpexs.decompiler.flash.tags.DefineSpriteTag
import com.jpexs.decompiler.flash.tags.Tag
import java.io.File

class Main {
    companion object {
        @JvmStatic
        fun main(args: Array<String>) {
            if (args.size < 2) {
                println("Usage: program <command>")
                return
            }
            try {
                runCommand(args)
            } catch (e: Exception) {
                println("Error: ${e.message}")
            }
        }

        private fun runCommand(args: Array<String>) {
            when (args[0]) {
                "merge" -> {
                    if (args.size != 4) {
                        println("Usage: program merge <original> <new> <output>")
                        return
                    }
                    File(args[1]).inputStream().use { originalStream ->
                        val original = SWF(originalStream, false)
                        File(args[2]).inputStream().use { newStream ->
                            val new = SWF(newStream, false)
                            merge(original, new)
                            save(original, File(args[3]))
                        }
                    }
                }

                "inject" -> {
                    if (args.size != 5) {
                        println("Usage: program inject <swf> <namespace> <name> <output>")
                        return
                    }
                    File(args[1]).inputStream().use { originalStream ->
                        val swf = SWF(originalStream, false)
                        inject(swf, getHelperClass(swf, args[2]), args[3])
                        save(swf, File(args[4]))
                    }
                }

                "info" -> {
                    if (args.size != 2) {
                        println("Usage: program info <file>")
                        return
                    }
                    File(args[1]).inputStream().use { stream ->
                        val swf = SWF(stream, false)
                        val json = "{" +
                                "\"version\" : ${swf.version}," +
                                "\"frame_rate\" : ${swf.frameRate}," +
                                "\"isAS3\" : ${swf.isAS3}," +
                                "\"width\" : ${swf.displayRect.width}," +
                                "\"height\" : ${swf.displayRect.height}" +
                                "}"
                        println(json)
                    }
                }

                else -> println("Unknown command ${args[0]}")
            }
        }

        private fun merge(original: SWF, new: SWF) {
            val al = original.abcList
            val firstAbc = al[0]

            original.debuggerPackage = "speculum"

            for (ds in new.abcList) {
                (ds as Tag).swf = original
                original.addTagBefore(ds, firstAbc as Tag)
                original.abcList.add(original.abcList.indexOf(firstAbc), ds)
                (ds as Tag).isModified = true

                val ft = original.fileAttributes
                ft.useNetwork = true
                ft.isModified = true
            }
        }

        private fun save(swf: SWF, file: File) {
            var swfToSave = swf
            if (swfToSave.gfx) {
                swfToSave = GfxConvertor().convertSwf(swf)
            }
            swfToSave.saveTo(file.outputStream())
        }

        private fun getHelperClass(swf: SWF, namespace: String): ScriptPack {
            val allAbcList: MutableList<ABC> = ArrayList()
            for (ac in swf.abcList) {
                allAbcList.add(ac.abc)
            }
            val list = ArrayList<ScriptPack>();
            for (ac in swf.abcList) {
                val a = ac.abc
                for (m in a.getScriptPacks(namespace, allAbcList)) {
                    if (m.classPath.packageStr.toRawString() == namespace) {
                        list.add(m)
                    }
                }
            }

            check(list.size != 0) { "Can not resolve $namespace" }
            check(list.size == 1) { "Multiple classes found for $namespace" }
            return list[0]
        }

        private fun inject(swf: SWF, pkg: ScriptPack, name: String) {
            val packageName = pkg.classPath.packageStr.toRawString()
            for (ct in swf.abcList) {
                val a = ct.abc
                if (a == pkg.abc) {
                    continue
                }
                val packageNs = a.constants.getNamespaceId(Namespace.KIND_PACKAGE, packageName, 0, true)
                for (i in 0 until a.constants.multinameCount) {
                    val m = a.constants.getMultiname(i) ?: continue
                    var rawNsName = m.getNameWithNamespace(a.constants, true).toRawString()
                    if (m.kind == Multiname.MULTINAME) {
                        val simpleName = m.getName(a.constants, ArrayList(), true, false)
                        if (simpleName != "") continue

                        for (ns in a.constants.getNamespaceSet(m.namespace_set_index).namespaces) {
                            if (a.constants.namespaceToString(ns) == "flash.net") {
                                m.kind = Multiname.QNAME
                                m.namespace_index = ns
                                m.namespace_set_index = 0
                                rawNsName = m.getNameWithNamespace(a.constants, true).toRawString()
                                break
                            }
                        }
                    }
                    when (rawNsName) {
                        "flash.net.URLLoader" -> {
                            m.namespace_index = packageNs
                            m.name_index = a.constants.getStringId(name, true)
                            (ct as Tag).isModified = true
                        }
                    }
                }
            }
        }
    }
}

private fun SWF.addTagBefore(newTag: Tag, targetTag: Tag) {
    val tim = targetTag.timelined
    val index = tim.indexOfTag(targetTag)
    if (index < 0) {
        return
    }
    tim.addTag(index, newTag)
    tim.resetTimeline()
    if (tim is DefineSpriteTag) {
        tim.frameCount = tim.getTimeline().frameCount
    } else if (tim is SWF) {
        tim.frameCount = tim.getTimeline().frameCount
    }
    newTag.timelined = tim
}
