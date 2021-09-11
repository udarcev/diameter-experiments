Этот проект показывает, как можно общаться с системой учета траффика мобильного оператора, используя протокол DIAMETER.

После установки pyDiameter надо изменить следующий файл

Поменять в файле pyDiaAVPBase.py
```python
retValue += encodedValue + NULL_BYTE * (self.getAlignmentLength(l) - l)
```
на
```python
retValue += encodedValue
if l != 0:
    retValue += NULL_BYTE * (self.getAlignmentLength(l) - l)
```

а то была бага в библиотеке при выравнивании значений с длиной поля равной 0 (то есть он просто закидывал 8 лишних байт)
